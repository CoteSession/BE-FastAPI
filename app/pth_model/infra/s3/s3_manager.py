import boto3
import logging
import os
from typing import List, Dict, Any
from fastapi import UploadFile
from botocore.exceptions import ClientError, NoCredentialsError

from app.pth_model.domain.repository.s3_manager_repo import IS3Manager

logger = logging.getLogger(__name__)


class S3Manager(IS3Manager):
    """
    S3 파일 업로드 관리자
    """
    
    def __init__(self):
        """
        S3 매니저 초기화 - 환경 변수에서 설정을 가져옵니다.
        """
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_REGION', 'ap-northeast-2')
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        
        # 필수 환경 변수 검증
        if not self.aws_access_key_id:
            raise ValueError("AWS_ACCESS_KEY_ID 환경 변수가 설정되지 않았습니다.")
        if not self.aws_secret_access_key:
            raise ValueError("AWS_SECRET_ACCESS_KEY 환경 변수가 설정되지 않았습니다.")
        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET_NAME 환경 변수가 설정되지 않았습니다.")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )
        
        logger.info(f"S3 매니저 초기화 완료 - 버킷: {self.bucket_name}, 리전: {self.region_name}")
    
    async def upload_files(self, files: List[UploadFile]) -> List[Dict[str, Any]]:
        """
        여러 파일을 S3에 업로드합니다.
        
        Args:
            files: 업로드할 파일 리스트
            
        Returns:
            List[Dict[str, Any]]: 업로드 결과 리스트
                각 딕셔너리는 다음 키를 포함:
                - filename: 원본 파일명
                - s3_key: S3에 저장된 키
                - file_size: 파일 크기
                - success: 업로드 성공 여부
                - error: 오류 메시지 (실패 시)
        """
        results = []
        
        for file in files:
            try:
                # 파일명에서 .pth 확장자 제거하여 모델명 추출
                model_name = file.filename.replace('.pth', '')
                s3_key = file.filename
                
                # 파일 내용 읽기
                file_content = await file.read()
                file_size = len(file_content)
                
                # S3에 업로드
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_content,
                    ContentType='application/octet-stream'
                )
                
                results.append({
                    'filename': file.filename,
                    'model_name': model_name,
                    's3_key': s3_key,
                    'file_size': file_size,
                    'success': True,
                    'error': None
                })
                
                logger.info(f"파일 업로드 성공: {file.filename} -> {s3_key}")
                
            except (ClientError, NoCredentialsError) as e:
                error_msg = f"S3 업로드 실패: {str(e)}"
                logger.error(f"{error_msg} - 파일: {file.filename}")
                
                results.append({
                    'filename': file.filename,
                    'model_name': file.filename.replace('.pth', ''),
                    's3_key': None,
                    'file_size': 0,
                    'success': False,
                    'error': error_msg
                })
        
        return results
    
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
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            file_data = response['Body'].read()
            logger.info(f"파일 다운로드 성공: {s3_key}")
            
            return file_data
            
        except (ClientError, NoCredentialsError) as e:
            error_msg = f"S3 다운로드 실패: {str(e)}"
            logger.error(f"{error_msg} - 파일: {s3_key}")
            raise Exception(error_msg)
    
    def test_connection(self) -> bool:
        """
        S3 연결을 테스트합니다.
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except (ClientError, NoCredentialsError):
            return False
