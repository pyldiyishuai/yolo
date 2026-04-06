import numpy as np
from services.detection_service import demo_detections, run_inference


def test_demo_detections_has_items():
    rows = demo_detections()
    assert isinstance(rows, list)
    assert len(rows) >= 1


def test_run_inference_returns_tuple():
    img = np.zeros((320, 320, 3), dtype=np.uint8)
    detections, fps = run_inference(img)
    assert isinstance(detections, list)
    assert isinstance(fps, float)
