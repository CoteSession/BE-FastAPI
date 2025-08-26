# FastAPI Backend

FastAPI를 사용한 백엔드 애플리케이션입니다.

## 기능

- 사용자 관리 (CRUD)
- 아이템 관리 (CRUD)
- JWT 인증
- SQLAlchemy ORM
- 자동 API 문서화
- S3 모델 파일 관리 (업로드/삭제)

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp env.example .env
```

`.env` 파일을 편집하여 필요한 설정을 변경하세요.

### 3. 데이터베이스 초기화

```bash
python init_database.py
```

### 4. 애플리케이션 실행

```bash
# 방법 1: app/main.py 직접 실행
python app/main.py

# 방법 2: uvicorn 사용 (권장)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 문서

애플리케이션 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
├── app/
│   ├── core/           # 핵심 설정 및 유틸리티
│   │   ├── config.py   # 애플리케이션 설정
│   │   ├── database.py # 데이터베이스 연결
│   │   └── security.py # 보안 유틸리티
│   ├── models/         # SQLAlchemy 모델
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/        # Pydantic 스키마
│   │   ├── user.py
│   │   └── item.py
│   ├── routers/        # API 라우터
│   │   ├── users.py
│   │   └── items.py
│   ├── main.py         # 애플리케이션 진입점
│   └── init_db.py      # 데이터베이스 초기화
├── pytorch_model/      # PyTorch 모델 관리
│   └── infra/          # 인프라 관련 코드
│       ├── s3_client.py    # S3 클라이언트
│       ├── s3_uploader.py  # S3 업로드 기능
│       ├── s3_deleter.py   # S3 삭제 기능
│       ├── s3_manager.py   # S3 통합 관리
│       └── example.py      # 사용 예제
├── init_database.py    # 데이터베이스 초기화 스크립트
├── requirements.txt    # 의존성 패키지
└── README.md
```

## API 엔드포인트

### 사용자 API

- `GET /api/v1/users/` - 사용자 목록 조회
- `GET /api/v1/users/{user_id}` - 특정 사용자 조회
- `POST /api/v1/users/` - 새 사용자 생성

### 아이템 API

- `GET /api/v1/items/` - 아이템 목록 조회
- `GET /api/v1/items/{item_id}` - 특정 아이템 조회
- `POST /api/v1/items/` - 새 아이템 생성

## 개발

### 테스트 실행

```bash
pytest
```

### 코드 포맷팅

```bash
black .
```

### 린팅

```bash
flake8 .
```

## S3 모델 관리

### 환경 변수 설정

```bash
export AWS_ACCESS_KEY_ID='your-access-key'
export AWS_SECRET_ACCESS_KEY='your-secret-key'
export S3_BUCKET_NAME='your-bucket-name'
```

### 사용 예제

```python
from pytorch_model.infra.s3_manager import S3Manager

# S3 매니저 초기화
s3_manager = S3Manager(
    aws_access_key_id='your-access-key',
    aws_secret_access_key='your-secret-key',
    bucket_name='your-bucket-name'
)

# 모델 파일 업로드
success = s3_manager.upload_model_file(
    model_path='path/to/model.pth',
    model_name='my_model',
    version='1.0.0'
)

# 모델 버전 삭제
success = s3_manager.delete_model_version('my_model', '1.0.0')

# 오래된 버전 정리 (최신 5개만 유지)
success = s3_manager.cleanup_old_versions('my_model', keep_versions=5)
```

### 예제 실행

```bash
cd pytorch_model/infra
python example.py
```
