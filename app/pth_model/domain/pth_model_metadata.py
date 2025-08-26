from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class PthModelMetadata:
    """
    S3에 저장된 PyTorch 모델 파일의 메타데이터를 위한 도메인 객체입니다.
    """
    # 필수 정보
    model_name: str
    s3_key: str
    file_size: int

    # 선택적 정보
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)