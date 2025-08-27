from datetime import datetime
from sqlalchemy import String, DateTime, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class PthModelMetadata(Base):
    """
    S3에 저장된 PyTorch 모델 파일의 메타데이터를 위한 테이블입니다.
    """
    __tablename__ = "pth_model_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    s3_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
