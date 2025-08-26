from abc import ABC, abstractmethod
from typing import List

from app.pth_model.domain.pth_model_metadata import PthModelMetadata


class IPthModelMetadataRepository(ABC):
    """
    PyTorch 모델 메타데이터 저장소 인터페이스
    """
    
    @abstractmethod
    async def create_model_metadata_batch(self, metadata_list: List[PthModelMetadata]) -> List[PthModelMetadata]:
        """
        여러 개의 모델 메타데이터를 배치로 저장하고 저장된 데이터를 반환합니다.

        Args:
            metadata_list (List[PthModelMetadata]): 저장할 모델 메타데이터 도메인 객체 리스트

        Returns:
            List[PthModelMetadata]: 저장된 모델 메타데이터 객체 리스트 (DB에서 생성된 ID 등 포함)
        """
        pass
