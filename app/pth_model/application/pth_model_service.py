from typing import List
from fastapi import UploadFile
from pydantic import BaseModel
import logging

from app.pth_model.domain.pth_model_metadata import PthModelMetadata
from app.pth_model.domain.repository.pth_model_metadata_reop import IPthModelMetadataRepository
from app.pth_model.domain.repository.s3_manager_repo import IS3Manager

logger = logging.getLogger(__name__)


class UploadModelResponse(BaseModel):
    """모델 업로드 응답"""
    success_count: int
    failed_count: int
    uploaded_files: List[PthModelMetadata]
    failed_files: List[str]


class ModelListResponse(BaseModel):
    """모델 목록 페이징 응답"""
    models: List[PthModelMetadata]
    current_page: int
    page_size: int
    total_count: int
    total_pages: int


class PthModelService:
    """
    PyTorch 모델 서비스
    """
    
    def __init__(self, metadata_repository: IPthModelMetadataRepository, s3_manager: IS3Manager):
        """
        서비스 초기화
        
        Args:
            metadata_repository: 메타데이터 저장소
            s3_manager: S3 매니저
        """
        self.s3_manager = s3_manager
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
    
    async def download_model_file(self, model_id: int) -> tuple[bytes, str]:
        """
        ID로 특정 PyTorch 모델 파일을 S3에서 다운로드합니다.
        
        Args:
            model_id: 다운로드할 모델의 ID
        
        Returns:
            tuple[bytes, str]: (파일 바이너리 데이터, 파일명)
        
        Raises:
            ValueError: 모델을 찾을 수 없는 경우
            Exception: S3 다운로드 실패 시
        """
        try:
            # 1. DB에서 모델 메타데이터 조회
            model_metadata = await self.metadata_repository.get_model_by_id(model_id)
            if not model_metadata:
                raise ValueError(f"ID {model_id}에 해당하는 모델을 찾을 수 없습니다.")
            
            # 2. S3에서 파일 다운로드
            file_data = await self.s3_manager.download_file(model_metadata.s3_key)
            filename = f"{model_metadata.model_name}.pth"
            
            logger.info(f"모델 ID {model_id} 파일 다운로드 완료: {filename}")
            
            return file_data, filename
            
        except ValueError as e:
            logger.error(f"모델 조회 실패: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"모델 파일 다운로드 중 오류 발생: {str(e)}")
            raise e
    
    async def get_model_list(self, page: int, page_size: int) -> ModelListResponse:
        """
        PyTorch 모델 목록을 페이징으로 조회합니다.
        
        Args:
            page: 페이지 번호 (1부터 시작)
            page_size: 페이지당 항목 수
        
        Returns:
            ModelListResponse: 페이징 정보가 포함된 모델 목록
        
        Raises:
            ValueError: 잘못된 페이징 파라미터
            Exception: DB 조회 실패 시
        """
        try:
            # 페이징 파라미터 검증
            if page < 1:
                raise ValueError("페이지 번호는 1 이상이어야 합니다.")
            if page_size < 1 or page_size > 100:
                raise ValueError("페이지 크기는 1 이상 100 이하여야 합니다.")
            
            # Repository에서 페이징 로직 호출
            offset = (page - 1) * page_size
            models = await self.metadata_repository.get_models_with_pagination(
                offset=offset, 
                limit=page_size
            )
            
            # 전체 개수 조회
            total_count = await self.metadata_repository.get_total_count()
            
            # 전체 페이지 수 계산
            total_pages = (total_count + page_size - 1) // page_size
            
            logger.info(f"모델 목록 조회 완료: page={page}, page_size={page_size}, 결과={len(models)}개, 전체={total_count}개")
            
            return ModelListResponse(
                models=models,
                current_page=page,
                page_size=page_size,
                total_count=total_count,
                total_pages=total_pages
            )
            
        except ValueError as e:
            logger.error(f"페이징 파라미터 오류: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"모델 목록 조회 중 오류 발생: {str(e)}")
            raise e
