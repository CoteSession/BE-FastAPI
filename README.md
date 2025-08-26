# FastAPI PyTorch Model Manager

FastAPI를 사용한 PyTorch 모델 파일 관리 백엔드 애플리케이션입니다.

## 기능

- PyTorch 모델 파일(.pth) S3 업로드/다운로드
- 모델 메타데이터 MySQL 데이터베이스 관리
- 페이징을 지원하는 모델 목록 조회
- Clean Architecture 패턴 적용
- Dependency Injection을 통한 의존성 관리
- 자동 API 문서화 (Swagger UI)

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 환경 변수를 설정하세요:

```bash
# MySQL 데이터베이스 설정
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/database_name

# AWS S3 설정
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-northeast-2
AWS_S3_BUCKET_NAME=your-bucket-name

# JWT 설정 (선택사항)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 데이터베이스 설정

MySQL 데이터베이스를 생성하고 연결 정보를 `.env` 파일에 설정하세요.

### 4. 애플리케이션 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 문서

애플리케이션 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
├── app/
│   ├── config/         # 애플리케이션 설정
│   │   └── settings.py # 환경 변수 및 설정 관리
│   ├── database/       # 데이터베이스 관련
│   │   └── db.py      # SQLAlchemy 설정 및 연결
│   ├── pth_model/      # PyTorch 모델 관리 모듈
│   │   ├── domain/     # 도메인 레이어
│   │   │   ├── pth_model_metadata.py           # 도메인 객체
│   │   │   └── repository/                     # 리포지토리 인터페이스
│   │   │       ├── pth_model_metadata_reop.py # 메타데이터 리포지토리 인터페이스
│   │   │       └── s3_manager_repo.py         # S3 매니저 인터페이스
│   │   ├── application/ # 애플리케이션 레이어
│   │   │   └── pth_model_service.py           # 비즈니스 로직
│   │   ├── interface/   # 인터페이스 레이어
│   │   │   └── controller/                     # API 컨트롤러
│   │   │       └── pth_model_controller.py    # PyTorch 모델 API
│   │   └── infra/      # 인프라 레이어
│   │       ├── db_models/                      # SQLAlchemy 모델
│   │       │   └── pth_model_metadata.py      # 메타데이터 DB 모델
│   │       ├── repository/                     # 리포지토리 구현체
│   │       │   └── pth_model_metadata_repo.py # 메타데이터 리포지토리
│   │       └── s3/                            # S3 관련
│   │           └── s3_manager.py              # S3 파일 관리
│   ├── containers.py   # Dependency Injection 컨테이너
│   └── main.py        # 애플리케이션 진입점
├── tests/             # 테스트 파일
│   └── test_s3_upload.py # S3 업로드 테스트
├── requirements.txt   # 의존성 패키지
└── README.md
```

## API 엔드포인트

### PyTorch 모델 관리 API

#### 1. 모델 파일 업로드

```
POST /api/v1/pytorch-models/upload
```

- **기능**: 여러 개의 `.pth` 파일을 S3에 업로드하고 메타데이터를 DB에 저장
- **요청**: `multipart/form-data`로 파일들 전송
- **응답**: 업로드 성공/실패 결과

**응답 예시:**

```json
{
  "success_count": 2,
  "failed_count": 0,
  "uploaded_files": [
    {
      "id": 1,
      "model_name": "model1",
      "s3_key": "model1.pth",
      "file_size": 1024,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "failed_files": []
}
```

#### 2. 모델 목록 조회 (페이징)

```
GET /api/v1/pytorch-models?page=1&page_size=10
```

- **기능**: 페이징으로 모델 목록 조회
- **파라미터**:
  - `page`: 페이지 번호 (1부터 시작, 기본값: 1)
  - `page_size`: 페이지당 항목 수 (기본값: 10, 최대: 100)

**응답 예시:**

```json
{
  "models": [
    {
      "id": 1,
      "model_name": "model1",
      "s3_key": "model1.pth",
      "file_size": 1024,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "current_page": 1,
  "page_size": 10,
  "total_count": 25,
  "total_pages": 3
}
```

#### 3. 모델 파일 다운로드

```
GET /api/v1/pytorch-models/{model_id}/download
```

- **기능**: ID로 특정 모델 파일을 S3에서 다운로드
- **응답**: 실제 `.pth` 파일 바이너리 데이터

## 아키텍처

### Clean Architecture 패턴

```
Interface Layer (Controller)
    ↓
Application Layer (Service)
    ↓
Domain Layer (Entities, Repository Interfaces)
    ↓
Infrastructure Layer (Repository Implementation, S3, DB)
```

### 의존성 주입

`app/containers.py`에서 Dependency Injection 컨테이너를 설정하여 의존성을 관리합니다.

## 개발

### 테스트 실행

```bash
# S3 연결 테스트
python tests/test_s3_upload.py
```

### 환경 변수 확인

API가 정상 작동하려면 다음 환경 변수가 설정되어 있어야 합니다:

- `AWS_ACCESS_KEY_ID`: AWS 액세스 키
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키
- `AWS_REGION`: AWS 리전 (기본값: ap-northeast-2)
- `AWS_S3_BUCKET_NAME`: S3 버킷 이름
- `DATABASE_URL`: MySQL 데이터베이스 연결 문자열

### 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 마이그레이션을 관리할 수 있습니다.

## 라이센스

MIT License
