import uuid
import time
from pathlib import Path
import cv2
import numpy as np
from config.settings import DEFAULT_MODEL_PATH
from config.object_labels import LABEL_ZH
from config.risk_rules import RISK_ORDER
from services.distance_estimator import estimate_distance
from services.direction_service import get_direction
from services.risk_service import assess_risk

_model = None
_model_path = Path(DEFAULT_MODEL_PATH)


def load_model():
    global _model
    if _model is not None:
        return _model
    try:
        from ultralytics import YOLO
        _model = YOLO(str(_model_path)) if _model_path.exists() else YOLO('yolov8n.pt')
        _model.to('cpu')
    except Exception:
        _model = None
    return _model


def preprocess(img_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError('无法解码图像')
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def demo_detections():
    return [
        {'id': str(uuid.uuid4())[:8], 'label': '行人', 'label_en': 'person', 'confidence': 0.93, 'distance': '中距离（约2.3m）', 'direction': '正前方', 'risk': 'medium'},
        {'id': str(uuid.uuid4())[:8], 'label': '汽车', 'label_en': 'car', 'confidence': 0.89, 'distance': '中距离（约5.2m）', 'direction': '右前方', 'risk': 'high'},
    ]


def run_inference(img):
    model = load_model()
    t0 = time.perf_counter()
    if model is None:
        return demo_detections(), 20.0
    results = model(img, conf=0.4, iou=0.5, verbose=False)
    fps = round(1.0 / max(time.perf_counter() - t0, 1e-6), 1)
    detections = []
    h, w = img.shape[:2]
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            raw_label = model.names.get(cls_id, 'unknown')
            label_zh = LABEL_ZH.get(raw_label, raw_label)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            bbox_h = y2 - y1
            cx = (x1 + x2) / 2
            detections.append({
                'id': str(uuid.uuid4())[:8],
                'label': label_zh,
                'label_en': raw_label,
                'confidence': round(float(box.conf[0]), 3),
                'distance': estimate_distance(bbox_h, raw_label, h),
                'direction': get_direction(cx, w),
                'risk': assess_risk(raw_label, bbox_h, h),
                'bbox': [round(x1), round(y1), round(x2), round(y2)],
            })
    detections.sort(key=lambda d: RISK_ORDER.get(d['risk'], 3))
    return detections, fps
