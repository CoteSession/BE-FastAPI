from typing import List
from fastapi import UploadFile
from pydantic import BaseModel
import logging

from app.pth_model.infra.s3.s3_manager import S3Manager
from app.pth_model.domain.pth_model_metadata import PthModelMetadata
from app.pth_model.domain.repository.pth_model_metadata_reop import IPthModelMetadataRepository

logger = logging.getLogger(__name__)


class UploadModelResponse(BaseModel):
    """모델 업로드 응답"""
    success_count: int
    failed_count: int
    uploaded_files: List[PthModelMetadata]
    failed_files: List[str]


class PthModelService:
    """
    PyTorch 모델 서비스
    """
    
    def __init__(self, metadata_repository: IPthModelMetadataRepository):
        """
        서비스 초기화
        
        Args:
            metadata_repository: 메타데이터 저장소
        """
        self.s3_manager = S3Manager()
        self.metadata_repository = metadata_repository
    
    async def upload_model_files(self, files: List[UploadFile]) -> UploadModelResponse:
        """
        여러 개의 PyTorch 모델 파일을 S3에 업로드하고 메타데이터를 DB에 저장합니다.
        
        Args:
            files: 업로드할 파일들 (파일명에서 모델 이름을 추출)
        
        Returns:
            UploadModelResponse: 업로드 결과
        """
        try:
            # 1. S3에 파일 업로드
            upload_results = await self.s3_manager.upload_files(files)
            
            # 2. 성공한 업로드 결과로 도메인 객체 생성
            successful_uploads = [result for result in upload_results if result['success']]
            
            if successful_uploads:
                # 3. 도메인 객체 리스트 생성
                metadata_list = []
                for result in successful_uploads:
                    metadata = PthModelMetadata(
                        model_name=result['model_name'],
                        s3_key=result['s3_key'],
                        file_size=result['file_size']
                    )
                    metadata_list.append(metadata)
                
                # 4. DB에 메타데이터 저장
                saved_metadata = await self.metadata_repository.create_model_metadata_batch(metadata_list)
                logger.info(f"메타데이터 DB 저장 완료: {len(saved_metadata)}개")
            
            # 5. 성공/실패 분류
            success_count = len(successful_uploads)
            failed_count = len(upload_results) - success_count
            
            # 6. 성공한 파일들의 PthModelMetadata 생성
            uploaded_files = []
            for result in successful_uploads:
                uploaded_files.append(PthModelMetadata(
                    model_name=result['model_name'],
                    s3_key=result['s3_key'],
                    file_size=result['file_size']
                ))
            
            # 7. 실패한 파일명들 수집
            failed_files = [
                result['filename'] 
                for result in upload_results 
                if not result['success']
            ]
            
            logger.info(f"모델 파일 업로드 완료: 성공 {success_count}개, 실패 {failed_count}개")
            
            return UploadModelResponse(
                success_count=success_count,
                failed_count=failed_count,
                uploaded_files=uploaded_files,
                failed_files=failed_files
            )
            
        except Exception as e:
            logger.error(f"모델 파일 업로드 중 오류 발생: {str(e)}")
            raise e
