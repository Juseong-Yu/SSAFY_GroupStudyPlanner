import asyncio
import logging
import uvicorn
from bot import bot
from api import app as fastapi_app
from worker import notice_worker
from config import BOT_API_HOST, BOT_API_PORT, BOT_TOKEN, LOG_LEVEL


logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("main")

async def start_uvicorn():
    """
    uvicorn.Server.serve()는 코루틴이므로 이벤트루프에 task로 등록 가능.
    앱이 단일 프로세스이므로 같은 루프에서 실행.
    """
    config = uvicorn.Config(
        fastapi_app,
        host=BOT_API_HOST,
        port=BOT_API_PORT,
        loop="asyncio",
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

def main():
    # 필수 환경 유무 확인
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN must be set in environment variables (.env or env)")

    loop = asyncio.get_event_loop()

    # 1) FastAPI를 백그라운드 task로 실행
    loop.create_task(start_uvicorn())

    # 2) discord bot 시작 (블로킹 역할이므로 loop.run_until_complete 사용)
    try:
        loop.run_until_complete(bot.start(BOT_TOKEN))
    except KeyboardInterrupt:
        logger.info("Shutdown requested via KeyboardInterrupt")
        loop.run_until_complete(bot.close())
    finally:
        # 안전한 종료를 위해 루프 닫기
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()

if __name__ == "__main__":
    main()