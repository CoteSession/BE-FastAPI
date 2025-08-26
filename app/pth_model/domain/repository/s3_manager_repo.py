from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from fastapi import UploadFile


class IS3Manager(ABC):
    """
    S3 파일 관리 인터페이스
    """
    
    @abstractmethod
    async def upload_files(self, files: List[UploadFile]) -> List[Dict[str, Any]]:
        """
        여러 파일을 S3에 업로드합니다.
        
        Args:
            files: 업로드할 파일 리스트
            
        Returns:
            List[Dict[str, Any]]: 업로드 결과 리스트
                각 딕셔너리는 다음 키를 포함:
                - filename: 원본 파일명
                - model_name: 모델명 (파일명에서 .pth 제거)
                - s3_key: S3에 저장된 키
                - file_size: 파일 크기
                - success: 업로드 성공 여부
                - error: 오류 메시지 (실패 시)
        """
        pass
    
    @abstractmethod
    async def download_file(self, s3_key: str) -> bytes:
        """
        S3에서 파일을 다운로드합니다.
        
        Args:
            s3_key: S3에 저장된 파일 키
            
        Returns:
            bytes: 파일 바이너리 데이터
            
        Raises:
            Exception: 파일 다운로드 실패 시
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        S3 연결을 테스트합니다.
        
        Returns:
            bool: 연결 성공 여부
        """
        pass
