from dependency_injector import containers, providers
from app.pth_model.application.pth_model_service import PthModelService
from app.pth_model.infra.s3.s3_manager import S3Manager
from app.pth_model.infra.repository.pth_model_metadata_repo import PthModelMetadataRepository


class Container(containers.DeclarativeContainer):
    """Dependency Injection 컨테이너"""
    
    # 설정
    config = providers.Configuration()
    
    # S3 매니저 (환경 변수에서 자동으로 설정 가져옴)
    s3_manager = providers.Singleton(S3Manager)
    
    # 메타데이터 저장소
    metadata_repository = providers.Singleton(PthModelMetadataRepository)
    
    # PyTorch 모델 서비스
    pth_model_service = providers.Factory(
        PthModelService,
        metadata_repository=metadata_repository
    )



