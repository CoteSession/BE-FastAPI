from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    PROJECT_NAME: str = "FastAPI PyTorch Model Manager"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "PyTorch 모델 파일을 S3에 업로드하고 관리하는 FastAPI 애플리케이션"
    API_V1_STR: str = "/api/v1"
    
    # 환경 설정
    ENVIRONMENT: str = "dev"  # dev 또는 prod
    DEBUG: bool = True
    
    # CORS 설정
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # MySQL 데이터베이스 설정
    DATABASE_URL: str
    
    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS S3 설정
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-northeast-2"
    AWS_S3_BUCKET_NAME: str
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경인지 확인"""
        return self.ENVIRONMENT == "prod"
    
    @property
    def is_development(self) -> bool:
        """개발 환경인지 확인"""
        return self.ENVIRONMENT == "dev"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()
