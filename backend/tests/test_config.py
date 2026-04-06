from config.object_labels import LABEL_ZH, HIGH_RISK_LABELS
from config.risk_rules import REAL_HEIGHT, RISK_ORDER


def test_core_config_loaded():
    assert LABEL_ZH['person'] == '行人'
    assert 'car' in HIGH_RISK_LABELS
    assert REAL_HEIGHT['person'] > 0
    assert RISK_ORDER['high'] == 0
