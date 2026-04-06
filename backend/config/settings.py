from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
MODEL_DIR = BASE_DIR / 'models'
DB_PATH = LOG_DIR / 'data.db'
EMERGENCY_LOG_PATH = LOG_DIR / 'emergency.log'
DEFAULT_MODEL_PATH = MODEL_DIR / 'yolov8n.pt'
API_PREFIX = '/api'
