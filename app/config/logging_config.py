import logging
import os
import platform
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class LevelFilter(logging.Filter):
   """특정 레벨만 통과시키는 필터"""
   def __init__(self, level):
       self.level = level
   
   def filter(self, record):
       return record.levelno == self.level

def create_timed_handler(log_dir, level_name, level):
   """공통 TimedRotatingFileHandler 생성 함수"""
   # 현재 날짜로 파일명 생성
   today = datetime.now().strftime('%Y-%m-%d')
   
   handler = TimedRotatingFileHandler(
       f'{log_dir}/{level_name.lower()}-{today}.log',  # info-2024-01-15.log 형식
       when='midnight',           # 자정마다 로테이션
       interval=1,               # 1일 간격
       backupCount=30,           # 30일 보관
       encoding='utf-8'
   )
   handler.suffix = '%Y-%m-%d'
   handler.addFilter(LevelFilter(level))
   
   # 포맷터 설정
   formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
   handler.setFormatter(formatter)
   
   return handler

def get_log_dir():
   """운영체제에 따른 로그 디렉토리 경로 반환"""
   if platform.system() == "Windows":
       return 'logs'  # 윈도우: 상대경로 (프로젝트 폴더 아래)
   else:
       return '/logs'  # Linux/Docker: 절대경로 (루트 아래)

def setup_logging():
   """환경에 따른 로깅 설정"""
   env = os.getenv('ENV', 'dev')
   print(f"현재 환경: {env}")
   print(f"현재 운영체제: {platform.system()}")
   
   if env == 'prod':
       # 프로덕션: 레벨별 파일 로깅 (Spring Boot 방식)
       log_dir = get_log_dir()
       print(f"로그 폴더 생성 위치: {os.path.abspath(log_dir)}")
       os.makedirs(log_dir, exist_ok=True)
       
       # 현재 날짜 (주석처리 - TimedRotatingFileHandler에서 자동 처리)
       # today = datetime.now().strftime('%Y-%m-%d')
       
       # 핸들러 생성 (공통 함수 사용)
       info_handler = create_timed_handler(log_dir, 'INFO', logging.INFO)
       warn_handler = create_timed_handler(log_dir, 'WARN', logging.WARNING)
       error_handler = create_timed_handler(log_dir, 'ERROR', logging.ERROR)
       
       # 로깅 설정
       logging.basicConfig(
           level=logging.INFO,
           handlers=[info_handler, warn_handler, error_handler],
           force=True
       )
       
   else:
       # 개발: 콘솔 로깅
       logging.basicConfig(
           level=logging.DEBUG,
           format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
           handlers=[
               logging.StreamHandler()
           ],
           force=True
       )

# def get_logger(name: str = __name__):
#     """로거 팩토리 함수"""
#     return logging.getLogger(name)