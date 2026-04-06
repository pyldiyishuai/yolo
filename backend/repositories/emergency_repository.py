import json
from config.settings import EMERGENCY_LOG_PATH

EMERGENCY_LOG_PATH.parent.mkdir(exist_ok=True)


def append_emergency_log(entry):
    with open(EMERGENCY_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def read_emergency_logs(limit=50):
    if not EMERGENCY_LOG_PATH.exists():
        return []
    rows = []
    with open(EMERGENCY_LOG_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    rows.reverse()
    return rows[:limit]
