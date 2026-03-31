# 视障人士环境感知与识别系统

基于改进 YOLOv8 + Vue3 + Python FastAPI 的本地部署视障辅助平台。

## 项目结构

```
yolo/
├── README.md
├── 需求文档.md
├── frontend/                    # Vue3 前端
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js           # Vite 配置，/api 代理至后端 8000 端口
│   └── src/
│       ├── main.js
│       ├── App.vue              # 全局布局、导航栏、预警悬浮层
│       ├── assets/main.css      # 全局样式（深蓝夜空 + 琥珀黄主题，高对比度）
│       ├── router/index.js
│       ├── stores/
│       │   ├── system.js        # 系统状态、TTS 播报、风险预警
│       │   ├── voice.js         # 语音识别，唤醒词「小视」
│       │   └── settings.js      # 本地设置持久化（localStorage）
│       └── views/
│           ├── HomeView.vue     # 主页：启动/停止、状态卡片、功能入口
│           ├── MonitorView.vue  # 环境监测：摄像头采集 + 实时识别结果
│           ├── SettingsView.vue # 设置：语音参数、紧急联系人、常用路线
│           └── EmergencyView.vue# 应急求助：SOS 大按钮、GPS 定位、求助记录
├── backend/                     # Python FastAPI 后端
│   ├── main.py                  # 服务入口，注册所有路由
│   ├── requirements.txt
│   ├── modules/
│   │   ├── detect.py            # YOLOv8 推理、距离估算、风险分级
│   │   ├── system.py            # 系统启动/停止/状态接口
│   │   ├── emergency.py         # 应急求助、短信通知（Twilio/阿里云）
│   │   └── data.py              # SQLite 识别日志与风险记录接口
│   ├── utils/
│   │   └── location.py          # Haversine 距离计算、路线偏离检测
│   ├── models/                  # 存放 .pt 模型文件（首次自动下载）
│   └── logs/                    # SQLite 数据库 + 应急日志
└── deploy/
    ├── config.ini               # 统一配置：端口、模型路径、短信服务
    ├── start.ps1                # Windows 一键启动脚本
    └── start.sh                 # Linux/macOS 一键启动脚本
```

## 项目文档

- [需求文档](./需求文档.md)：用于后续功能迭代、版本规划、测试验收与答辩材料整理

## 快速启动

### 方式一：手动启动（推荐开发调试）

**第一步：安装后端依赖**

```powershell
cd backend
# 如系统配置了代理，需将 HTTPS_PROXY 改为 http:// 协议头
$env:HTTPS_PROXY='http://127.0.0.1:7897'
$env:HTTP_PROXY='http://127.0.0.1:7897'
python -m pip install -r requirements.txt
```

**第二步：启动后端**

```powershell
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

**第三步：启动前端（另开终端）**

```powershell
npm install
cd frontend
npm run dev
```

访问 http://localhost:5173 打开系统界面。

### 方式二：Windows 一键启动

```powershell
powershell -ExecutionPolicy Bypass -File deploy\start.ps1
```

> **代理说明**：若本机使用代理（如 Clash），请确保代理地址以 `http://` 开头而非 `https://`，否则 pip 会报 `check_hostname` 错误。

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端 API | http://127.0.0.1:8000 |
| API 交互文档 | http://127.0.0.1:8000/docs |

## 核心功能

| 模块 | 说明 |
|------|------|
| 环境监测 | 调用摄像头实时采集，YOLOv8 推理识别盲道/障碍物/行人/车辆，自动估算距离与风险等级 |
| 语音交互 | 浏览器原生 SpeechRecognition，唤醒词「小视」，支持启动/关闭/求助/设置等语音指令 |
| 风险预警 | 高/中/低三级风险评级，高风险自动语音播报 + 全局预警悬浮提示 |
| 应急求助 | 一键或语音触发，获取 GPS 位置，通知紧急联系人（支持 Twilio/阿里云短信） |
| 本地设置 | 语速/音量/联系人/路线存储于 localStorage，无需联网，断电不丢失 |
| 日志存储 | 识别记录与风险日志保存至本地 SQLite，无需部署数据库 |

## 配置短信通知（可选）

编辑 `deploy/config.ini`，修改 `[sms]` 段：

```ini
[sms]
; 可选: none / twilio / aliyun
provider = twilio
account_sid = ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
auth_token  = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
from_number = +1xxxxxxxxxx
```

未配置时系统仍正常运行，仅本地语音播报预警，不影响其他功能。

## YOLOv8 模型说明

- 后端首次调用 `/api/detect` 接口时，若 `backend/models/yolov8n.pt` 不存在，将自动从网络下载（约 6MB）
- 未安装 `ultralytics` 或模型下载失败时，系统自动进入 **Demo 模式**，返回模拟识别数据，前端功能不受影响
- 如需使用自训练模型，将 `.pt` 文件放入 `backend/models/` 并在 `deploy/config.ini` 中修改 `model_file` 路径

## 无障碍特性

- 全站语义化 HTML（ARIA 标签、`role`、`aria-live` 动态区域）
- 高对比度配色：深蓝夜空底色 + 琥珀黄主色，符合 WCAG AA 标准
- 大字体（基准 18px）、大按钮（最小 56px 高），适配触屏操作
- 兼容 NVDA / VoiceOver 屏幕阅读器
- 键盘完全可操作，焦点轮廓清晰可见
- 语音控制与 TTS 播报使用浏览器原生 API，无需额外安装

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router + Axios |
| 后端 | Python 3.10+ / FastAPI / Uvicorn |
| 视觉识别 | Ultralytics YOLOv8n + OpenCV（CLAHE 低光照增强） |
| 数据存储 | localStorage（前端配置）+ SQLite（后端日志） |
| 部署 | 全本地，无需服务器或云服务 |

## 阅读建议

- 首次了解项目：先阅读 `README.md`
- 需要继续扩展功能、撰写答辩材料或拆分版本：阅读 `需求文档.md`
- 需要定位实现细节：进入 `frontend/` 与 `backend/` 对应模块查看代码
