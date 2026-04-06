from fastapi import APIRouter, UploadFile, File, HTTPException
from services.detection_service import preprocess, run_inference

router = APIRouter()


@router.post('/detect')
async def detect(file: UploadFile = File(...)):
    if file.content_type and 'image' not in file.content_type:
        raise HTTPException(status_code=400, detail='请上传图像文件')
    img_bytes = await file.read()
    try:
        img = preprocess(img_bytes)
        detections, fps = run_inference(img)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {'detections': detections, 'fps': fps, 'count': len(detections)}
