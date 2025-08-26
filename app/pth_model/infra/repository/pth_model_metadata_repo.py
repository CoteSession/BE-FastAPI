from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging

from app.pth_model.domain.pth_model_metadata import PthModelMetadata
from app.pth_model.domain.repository.pth_model_metadata_reop import IPthModelMetadataRepository
from app.pth_model.infra.db_models.pth_model_metadata import PthModelMetadata as PthModelMetadataModel
from app.database.db import get_db

logger = logging.getLogger(__name__)


class PthModelMetadataRepository(IPthModelMetadataRepository):
    """
    PyTorch 모델 메타데이터 저장소 구현체
    """
    
    async def create_model_metadata_batch(self, metadata_list: List[PthModelMetadata]) -> List[PthModelMetadata]:
        """
        여러 개의 모델 메타데이터를 배치로 저장하고 저장된 데이터를 반환합니다.

        Args:
            metadata_list (List[PthModelMetadata]): 저장할 모델 메타데이터 도메인 객체 리스트

        Returns:
            List[PthModelMetadata]: 저장된 모델 메타데이터 객체 리스트 (DB에서 생성된 ID 등 포함)

        Raises:
            SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
        """
        async for db in get_db():
            try:
                # 배치 변환
                metadata_models = self._convert_to_models_batch(metadata_list)

                # 배치 추가
                db.add_all(metadata_models)

                # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
                await db.flush()

                logger.debug("Flush 후 저장된 메타데이터 ID: %s", [metadata.id for metadata in metadata_models])
                logger.debug("Flush 후 저장된 모델명: %s", [metadata.model_name for metadata in metadata_models])

                # 저장된 모델들을 배치로 도메인 객체 변환
                saved_metadata_vos = self._convert_to_domains_batch(metadata_models)

                logger.debug("도메인 객체 변환 후 메타데이터 ID: %s", [vo.id for vo in saved_metadata_vos])
                logger.debug("도메인 객체 변환 후 모델명: %s", [vo.model_name for vo in saved_metadata_vos])

                # 최종 커밋
                await db.commit()

                logger.debug("Commit 완료")

                return saved_metadata_vos

            except SQLAlchemyError as e:
                await db.rollback()
                logger.error("DB 저장 중 오류 발생: %s", e)
                raise e

    async def get_model_by_id(self, model_id: int) -> Optional[PthModelMetadata]:
        """
        ID로 특정 모델 메타데이터를 조회합니다.

        Args:
            model_id (int): 조회할 모델의 ID

        Returns:
            Optional[PthModelMetadata]: 조회된 모델 메타데이터 (없으면 None)

        Raises:
            SQLAlchemyError: 데이터베이스 조회 중 오류 발생 시
        """
        async for db in get_db():
            try:
                result = await db.execute(
                    select(PthModelMetadataModel).where(PthModelMetadataModel.id == model_id)
                )
                model = result.scalar_one_or_none()
                
                if model is None:
                    return None
                
                # 도메인 객체로 변환
                return PthModelMetadata(
                    id=model.id,
                    model_name=model.model_name,
                    s3_key=model.s3_key,
                    file_size=model.file_size,
                    created_at=model.created_at
                )
                
            except SQLAlchemyError as e:
                logger.error("DB 조회 중 오류 발생: %s", e)
                raise e
    
    async def get_models_with_pagination(self, offset: int, limit: int) -> List[PthModelMetadata]:
        """
        페이징을 사용하여 모델 메타데이터 목록을 조회합니다.

        Args:
            offset (int): 건너뛸 레코드 수
            limit (int): 조회할 레코드 수

        Returns:
            List[PthModelMetadata]: 모델 메타데이터 목록 (최신순)

        Raises:
            SQLAlchemyError: 데이터베이스 조회 중 오류 발생 시
        """
        async for db in get_db():
            try:
                result = await db.execute(
                    select(PthModelMetadataModel)
                    .order_by(PthModelMetadataModel.id.desc())  # 최신순 정렬
                    .offset(offset)
                    .limit(limit)
                )
                models = result.scalars().all()
                
                # 도메인 객체로 변환
                return self._convert_to_domains_batch(models)
                
            except SQLAlchemyError as e:
                logger.error("DB 페이징 조회 중 오류 발생: %s", e)
                raise e
    
    async def get_total_count(self) -> int:
        """
        전체 모델 개수를 조회합니다.

        Returns:
            int: 전체 모델 개수

        Raises:
            SQLAlchemyError: 데이터베이스 조회 중 오류 발생 시
        """
        async for db in get_db():
            try:
                result = await db.execute(
                    select(func.count(PthModelMetadataModel.id))
                )
                total_count = result.scalar()
                return total_count
                
            except SQLAlchemyError as e:
                logger.error("DB 전체 개수 조회 중 오류 발생: %s", e)
                raise e

                
    def _convert_to_models_batch(self, metadata_vos: List[PthModelMetadata]) -> List[PthModelMetadataModel]:
        """
        Domain Entity를 SQLAlchemy Model로 배치 변환합니다.
        
        Args:
            metadata_vos (List[PthModelMetadata]): 변환할 메타데이터 도메인 객체 리스트
            
        Returns:
            List[PthModelMetadataModel]: SQLAlchemy 모델 객체 리스트
        """
        models = []
        for vo in metadata_vos:
            model_data = {
                'model_name': vo.model_name,
                's3_key': vo.s3_key,
                'file_size': vo.file_size,
                'created_at': vo.created_at
            }
            # id가 있는 경우에만 추가
            if vo.id is not None:
                model_data['id'] = vo.id
            models.append(PthModelMetadataModel(**model_data))
        return models

    def _convert_to_domains_batch(self, metadata_models: List[PthModelMetadataModel]) -> List[PthModelMetadata]:
        """
        SQLAlchemy Model을 Domain Entity로 배치 변환합니다.
        
        Args:
            metadata_models (List[PthModelMetadataModel]): 변환할 SQLAlchemy 모델 객체 리스트
            
        Returns:
            List[PthModelMetadata]: 메타데이터 도메인 객체 리스트
        """
        return [
            PthModelMetadata(
                id=model.id,
                model_name=model.model_name,
                s3_key=model.s3_key,
                file_size=model.file_size,
                created_at=model.created_at
            )
            for model in metadata_models
        ]
    
