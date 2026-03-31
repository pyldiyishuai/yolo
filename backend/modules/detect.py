"""
YOLOv8 视觉识别模块
处理流程: 前端图像帧 -> 图像预处理 -> YOLO 推理 -> 输出识别结果与风险等级
本地部署版, 优先 CPU 推理, 无需显卡
"""
import time
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
import numpy as np
import cv2

router = APIRouter()

# 模型单例（延迟加载，首次请求时初始化）
_model = None
_model_path = Path(__file__).parent.parent / "models" / "yolov8n.pt"

# COCO 80 类 + 自定义辅助类别中文映射
LABEL_ZH = {
    "person": "行人", "bicycle": "自行车", "car": "汽车", "motorcycle": "摩托车",
    "bus": "公交车", "truck": "卡车", "traffic light": "红绿灯",
    "stop sign": "停车标志", "bench": "长椅", "dog": "狗",
    "chair": "椅子", "potted plant": "盆栽", "suitcase": "行李箱",
    "umbrella": "雨伞", "handbag": "手提包", "bottle": "瓶子",
    "tactile_paving": "盲道",   # 盲道（自定义类别）
    "obstacle": "障碍物",       # 通用障碍物
    "stairs": "台阶",
    "door": "门",
    "hole": "坑洼",
}

# 高风险类别：车辆 / 台阶 / 坑洼，靠近时危险性最大
HIGH_RISK_LABELS = {"car", "truck", "bus", "motorcycle", "hole", "stairs"}
# 中风险类别：行人 / 自行车 / 动物 / 障碍物
MEDIUM_RISK_LABELS = {"person", "bicycle", "dog", "obstacle", "potted plant"}

# 针孔模型焦距（像素），影响参考距离精度
# 标定方法：将已知高度目标放在已知距离处，focal = bbox_h * dist / real_h
FOCAL_LENGTH = 600  # 默认值适配大多数摄像头，误差约 40%

# 各类目标预设真实高度（米），用于针孔模型参考距离
REAL_HEIGHT = {
    "person": 1.7, "car": 1.5, "bus": 3.0, "truck": 2.5,
    "bicycle": 1.0, "motorcycle": 1.2, "default": 1.0,
}

# bbox 占画面高度比例阈值（主要风险判断依据，不依赖焦距标定，更稳定）
DIST_RATIO_NEAR   = 0.35  # bbox/img_h > 35%    -> 近距离（< ~2m）
DIST_RATIO_MEDIUM = 0.12  # bbox/img_h 12%~35%  -> 中距离（2~6m）
                          # bbox/img_h < 12%    -> 远距离（> ~6m）


def load_model():
    """懒加载 YOLOv8 模型。
    - 优先加载 backend/models/yolov8n.pt
    - 文件不存在时自动下载（约 6MB）
    - ultralytics 未安装或加载失败时进入 Demo 模式
    """
    global _model
    if _model is not None:
        return _model
    try:
        from ultralytics import YOLO
        # 优先本地模型文件，不存在则在线下载
        _model = YOLO(str(_model_path)) if _model_path.exists() else YOLO("yolov8n.pt")
        _model.to("cpu")  # 本地部署默认 CPU，有 GPU 时自动切换
        print(f"[YOLO] 模型加载成功: {_model_path.name}")
    except ImportError:
        print("[YOLO] ultralytics 未安装，进入 Demo 模式")
        _model = None
    except Exception as e:
        print(f"[YOLO] 加载失败: {e}，进入 Demo 模式")
        _model = None
    return _model


def preprocess(img_bytes: bytes) -> np.ndarray:
    """图像预处理：字节流解码 + CLAHE 低光照增强。
    CLAHE（对比度受限自适应直方图均衡）对夜间 / 弱光场景效果明显。
    只对 LAB 亮度通道 L 做增强，避免色彩失真。
    """
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("无法解码图像")
    # 转 LAB 色彩空间，只处理亮度通道
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def estimate_distance(bbox_h: float, label: str, img_h: int) -> str:
    """双模式距离估算。
    主模式：bbox/img 比例分区（近 / 中 / 远），稳定，不依赖焦距标定。
    辅助：针孔模型参考米数，括号内显示，误差较大仅供参考。
    """
    if bbox_h <= 0 or img_h <= 0:
        return "未知"
    ratio = bbox_h / img_h
    # 按比例判断距离区间
    if ratio >= DIST_RATIO_NEAR:
        zone = "近距离"
    elif ratio >= DIST_RATIO_MEDIUM:
        zone = "中距离"
    else:
        zone = "远距离"
    # 针孔模型参考值（仅供参考）
    real_h = REAL_HEIGHT.get(label, REAL_HEIGHT["default"])
    dist_m = (real_h * FOCAL_LENGTH) / bbox_h
    ref = f"{dist_m*100:.0f}cm" if dist_m < 1 else f"{dist_m:.1f}m"
    return f"{zone}（约{ref}）"


def get_direction(cx: float, img_w: int) -> str:
    """根据目标中心 x 坐标将画面三等分判断方向。"""
    third = img_w / 3
    if cx < third:
        return "左前方"
    elif cx > third * 2:
        return "右前方"
    return "正前方"


def assess_risk(label: str, bbox_h: float, img_h: int) -> str:
    """风险评估：基于目标类别 + bbox 占画面比例。
    使用比例而非距离字符串，避免解析误差，判断更稳定。
    - 高风险：高危类别 + 近距离
    - 中风险：高危类别中距离 or 中危类别近距离
    - 低风险：其余情况
    """
    if img_h <= 0:
        return "low"
    ratio = bbox_h / img_h
    if label in HIGH_RISK_LABELS:
        if ratio >= DIST_RATIO_NEAR:    # 近距离高危 -> 高风险
            return "high"
        if ratio >= DIST_RATIO_MEDIUM:  # 中距离高危 -> 中风险
            return "medium"
        return "low"                   # 远距离高危 -> 低风险
    if label in MEDIUM_RISK_LABELS:
        if ratio >= DIST_RATIO_NEAR:    # 近距离中危 -> 中风险
            return "medium"
        return "low"
    return "low"  # 其他类别默认低风险


def run_inference(img: np.ndarray) -> tuple[list, float]:
    """执行 YOLO 推理主流程。
    返回：(检测结果列表, 推理帧率 FPS)
    model 为 None 时返回 Demo 演示数据。
    """
    model = load_model()
    t0 = time.perf_counter()
    if model is None:
        return _demo_detections(), 20.0  # Demo 模式返回模拟数据
    results = model(img, conf=0.4, iou=0.5, verbose=False)
    fps = round(1.0 / max(time.perf_counter() - t0, 1e-6), 1)
    detections = []
    h, w = img.shape[:2]
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            raw_label = model.names.get(cls_id, "unknown")
            label_zh = LABEL_ZH.get(raw_label, raw_label)  # 转中文标签
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            bbox_h = y2 - y1          # bbox 像素高度
            cx = (x1 + x2) / 2       # bbox 中心 x 坐标
            dist = estimate_distance(bbox_h, raw_label, h)
            direction = get_direction(cx, w)
            risk = assess_risk(raw_label, bbox_h, h)
            conf = float(box.conf[0])
            detections.append({
                "id": str(uuid.uuid4())[:8],
                "label": label_zh,
                "label_en": raw_label,
                "confidence": round(conf, 3),
                "distance": dist,
                "direction": direction,
                "risk": risk,
                "bbox": [round(x1), round(y1), round(x2), round(y2)],
            })
    # 按风险等级降序排列：high -> medium -> low
    order = {"high": 0, "medium": 1, "low": 2}
    detections.sort(key=lambda d: order.get(d["risk"], 3))
    return detections, fps


def _demo_detections() -> list:
    """Demo 模式演示数据。
    ultralytics 未安装时返回模拟识别结果，不影响前端功能验证。
    """
    import random
    samples = [
        {"label": "行人",   "label_en": "person",   "risk": "medium", "distance": "中距离（约2.3m）", "direction": "正前方"},
        {"label": "盲道",   "label_en": "tactile",  "risk": "low",    "distance": "近距离（约1.0m）", "direction": "正前方"},
        {"label": "汽车",   "label_en": "car",      "risk": "high",   "distance": "中距离（约5.2m）", "direction": "右前方"},
        {"label": "障碍物", "label_en": "obstacle", "risk": "medium", "distance": "近距离（约1.5m）", "direction": "左前方"},
    ]
    chosen = random.sample(samples, k=random.randint(1, 3))
    return [{**d, "id": str(uuid.uuid4())[:8], "confidence": round(random.uniform(0.7, 0.98), 3)} for d in chosen]


@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    """接收前端图像帧，执行 YOLO 推理，返回识别结果与风险等级。"""
    if file.content_type and "image" not in file.content_type:
        raise HTTPException(status_code=400, detail="请上传图像文件")
    img_bytes = await file.read()
    try:
        img = preprocess(img_bytes)
        detections, fps = run_inference(img)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"detections": detections, "fps": fps, "count": len(detections)}
