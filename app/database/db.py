import logging
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

# 로깅 설정: SQLAlchemy 쿼리 로그 끄기 (echo=True 상태에서도)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# .env 파일 로드
load_dotenv()

# 환경 변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# Base 선언 (모든 모델의 베이스 클래스)
Base = declarative_base()

# 비동기 SQLAlchemy 엔진 설정
engine = create_async_engine(
    DATABASE_URL,               # 데이터베이스 접속 URL
    echo=False,                 # SQL 쿼리를 로그로 출력할지 여부 (디버깅용)
    pool_size=7,               # 커넥션 풀의 기본 연결 수 (초기 커넥션 수)
    max_overflow=20,            # 풀 외에 추가로 허용할 커넥션 수 (최대 10 + 20 = 30까지 가능)
    pool_recycle=1800,          # 30분(1800초) 마다 커넥션 재활용 (MySQL의 timeout 방지 등)
    pool_pre_ping=True          # 커넥션 사용 전 유효한지 검사하여 끊긴 커넥션 자동 복구
)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# get_db() 함수 (의존성 주입용)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
