import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.logging_config import setup_logging
from app.pth_model.interface.controller.pth_model_controller import router as pth_model_router
from app.containers import Container

# 로깅 설정 초기화
setup_logging()

logger = logging.getLogger(__name__)

# 애플리케이션 시작 로그
logger.info("FastAPI 애플리케이션 시작")
logger.warning("이것은 경고 로그입니다")
logger.error("이것은 에러 로그입니다")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Injection 컨테이너 설정
container = Container()
app.container = container

# 컨테이너 wiring 설정 (모든 모듈에 대해)
container.wire(modules=["app.pth_model.interface.controller.pth_model_controller"])

# API 라우터 등록
app.include_router(pth_model_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    logger.info("루트 엔드포인트 호출됨")
    return {"message": "FastAPI 애플리케이션에 오신 것을 환영합니다!"}

@app.get("/health")
async def health_check():
    logger.info("헬스 체크 엔드포인트 호출됨")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
