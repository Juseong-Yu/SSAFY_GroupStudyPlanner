import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

# 디스코드 봇 토큰
BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")

# FastAPI(봇 API) 바인드 정보
BOT_API_HOST: str = os.getenv("BOT_API_HOST", "0.0.0.0")
BOT_API_PORT: int = int(os.getenv("BOT_API_PORT", "8001"))

# Django와 공유하는 간단한 인증 시크릿
BOT_API_SECRET: str = os.getenv("BOT_API_SECRET", "supersecret")

# 로깅 레벨
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# 워커 전송 재시도 수
MAX_SEND_RETRIES: int = int(os.getenv("MAX_SEND_RETRIES", "3"))

# 타임아웃 설정 (Django에서 bot API 호출 시 권장)
DEFAULT_HTTP_TIMEOUT: int = int(os.getenv("DEFAULT_HTTP_TIMEOUT", "2"))