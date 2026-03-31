"""
视助系统后端入口 - FastAPI
本地部署版，无需外部数据库，运行即用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from modules.detect import router as detect_router
from modules.system import router as system_router
from modules.emergency import router as emergency_router
from modules.data import router as data_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[视助系统] 后端服务启动成功，监听 http://127.0.0.1:8000")
    yield
    print("[视助系统] 后端服务已关闭")


app = FastAPI(
    title="视助系统 API",
    description="基于改进 YOLOv8 的视障人士环境感知系统后端接口",
    version="1.0.0",
    lifespan=lifespan,
)

# 跨域支持（适配本地 Vue3 前端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(detect_router,    prefix="/api", tags=["识别"])
app.include_router(system_router,    prefix="/api", tags=["系统"])
app.include_router(emergency_router, prefix="/api", tags=["应急"])
app.include_router(data_router,      prefix="/api", tags=["数据"])


@app.get("/api/ping", tags=["系统"])
async def ping():
    return {"status": "ok", "message": "视助系统后端运行正常"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
