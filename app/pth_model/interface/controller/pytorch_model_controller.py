from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
from app.containers import Container

from app.pth_model.application.pth_model_service import PthModelService, UploadModelResponse

router = APIRouter(prefix="/pytorch-models")


@router.post("/upload", status_code=201, response_model=UploadModelResponse)
@inject
async def upload_model_files(
    files: List[UploadFile] = File(...),
    pth_model_service: PthModelService = Depends(Provide[Container.pth_model_service]),
):
    """
    여러 개의 PyTorch 모델 파일(.pth)을 업로드합니다.
    
    Args:
        files: 업로드할 .pth 파일들
        pytorch_model_service: PyTorch 모델 서비스
    
    Returns:
        UploadModelResponse: 업로드 결과
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드할 파일이 없습니다."
        )
    
    # .pth 파일만 허용
    for file in files:
        if not file.filename.endswith('.pth'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 형식입니다: {file.filename}. .pth 파일만 업로드 가능합니다."
            )
    
    try:
        result = await pth_model_service.upload_model_files(
            files=files
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 파일 업로드 중 오류가 발생했습니다: {str(e)}"
        )
