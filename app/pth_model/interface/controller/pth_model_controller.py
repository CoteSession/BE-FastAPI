from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Response, Query
from typing import List
from app.containers import Container

from app.pth_model.application.pth_model_service import PthModelService, UploadModelResponse, ModelListResponse
from app.pth_model.domain.pth_model_metadata import PthModelMetadata

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


@router.get("/{model_id}/download")
@inject
async def download_model_file(
    model_id: int,
    pth_model_service: PthModelService = Depends(Provide[Container.pth_model_service]),
):
    """
    ID로 특정 PyTorch 모델 파일을 S3에서 다운로드합니다.
    
    Args:
        model_id: 다운로드할 모델의 ID
        pth_model_service: PyTorch 모델 서비스
    
    Returns:
        Response: .pth 파일 바이너리 데이터
    """
    try:
        file_data, filename = await pth_model_service.download_model_file(model_id)
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {model_id}에 해당하는 모델 파일을 찾을 수 없습니다."
            )
        
        return Response(
            content=file_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/octet-stream"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 파일 다운로드 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("", response_model=ModelListResponse)
@inject
async def get_model_list(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(10, ge=1, le=100, description="페이지당 항목 수 (최대 100개)"),
    pth_model_service: PthModelService = Depends(Provide[Container.pth_model_service]),
):
    """
    PyTorch 모델 목록을 페이징으로 조회합니다.
    
    Args:
        page: 페이지 번호 (1부터 시작)
        page_size: 페이지당 항목 수 (기본값: 10, 최대: 100)
        pth_model_service: PyTorch 모델 서비스
    
    Returns:
        ModelListResponse: 페이징 정보가 포함된 모델 목록
            - models: 모델 메타데이터 목록
            - current_page: 현재 페이지 번호
            - page_size: 페이지당 항목 수
            - total_count: 전체 모델 개수
            - total_pages: 전체 페이지 수
    """
    try:
        result = await pth_model_service.get_model_list(page=page, page_size=page_size)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )



