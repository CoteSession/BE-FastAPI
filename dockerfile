# ✅ 1단계: 빌드용 이미지
FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive

# 빌드에 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install

COPY requirements.txt .

# pip 업그레이드 및 패키지 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

#------------#

# ✅ 2단계: 실행용 경량 이미지
FROM python:3.11-slim

WORKDIR /code

# 빌더에서 패키지만 복사
COPY --from=builder /usr/local /usr/local

# 앱 소스 복사
COPY . /code

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]

