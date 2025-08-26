import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

# 환경 변수 로드
load_dotenv()

from pth_model.infra.s3.s3_manager import S3Manager

async def test_s3_connection():
    """S3 연결 테스트"""
    print("🔍 S3 연결 테스트 중...")
    
    try:
        s3_manager = S3Manager()
        is_connected = s3_manager.test_connection()
        
        if is_connected:
            print("✅ S3 연결 성공!")
            print(f"   버킷: {s3_manager.bucket_name}")
            print(f"   리전: {s3_manager.region_name}")
        else:
            print("❌ S3 연결 실패!")
            
    except Exception as e:
        print(f"❌ S3 연결 오류: {str(e)}")

async def test_file_upload():
    """파일 업로드 테스트"""
    print("\n📤 파일 업로드 테스트 중...")
    
    try:
        # 테스트용 더미 파일 생성
        test_files = []
        test_dir = Path("tests/test_files")
        test_dir.mkdir(exist_ok=True, parents=True)
        
        # 더미 .pth 파일들 생성
        for i in range(3):
            file_path = test_dir / f"test_model_{i+1}.pth"
            with open(file_path, 'wb') as f:
                f.write(b"dummy pytorch model data" * 100)  # 더미 데이터
            test_files.append(file_path)
        
        print(f"   생성된 테스트 파일: {[f.name for f in test_files]}")
        
        # S3 매니저로 업로드 테스트
        s3_manager = S3Manager()
        
        # UploadFile 객체 시뮬레이션
        from fastapi import UploadFile
        from io import BytesIO
        
        upload_files = []
        for file_path in test_files:
            with open(file_path, 'rb') as f:
                content = f.read()
                upload_file = UploadFile(
                    filename=file_path.name,
                    file=BytesIO(content)
                )
                upload_files.append(upload_file)
        
        # 업로드 실행
        results = await s3_manager.upload_files(upload_files)
        
        # 결과 출력
        success_count = sum(1 for r in results if r['success'])
        print(f"   업로드 결과: 성공 {success_count}개, 실패 {len(results) - success_count}개")
        
        for result in results:
            if result['success']:
                print(f"   ✅ {result['filename']} -> {result['s3_key']}")
            else:
                print(f"   ❌ {result['filename']}: {result['error']}")
        
        # 테스트 파일 정리
        for file_path in test_files:
            file_path.unlink()
        test_dir.rmdir()
        
    except Exception as e:
        print(f"❌ 파일 업로드 테스트 오류: {str(e)}")

async def main():
    """메인 테스트 함수"""
    print("🚀 S3 업로드 기능 테스트 시작\n")
    
    # 1. S3 연결 테스트
    await test_s3_connection()
    
    # 2. 파일 업로드 테스트
    await test_file_upload()
    
    print("\n✨ 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
