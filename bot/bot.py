import asyncio
import logging
from discord.ext import commands
import discord
from config import LOG_LEVEL
from worker import notice_worker

# 로거 (모듈 단위 로깅)
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("bot")

# 필요한 intents 설정
intents = discord.Intents.default()
# 메시지 내용 접근을 원치 않으므로 기본으로 둠
intents.message_content = False

# Bot 인스턴스 (command_prefix는 향후 명령어 확장 시 사용)
bot = commands.Bot(command_prefix="!", intents=intents)

# 전역 비동기 큐: api.py 에서 put(), worker.py 에서 get()
notice_queue: asyncio.Queue = asyncio.Queue()

@bot.event
async def on_ready():
    print(f"Discord bot connected: {bot.user}")
    logger.info("Discord bot connected: %s#%s", bot.user.name, bot.user.discriminator)

    # 봇 연결 완료 시 한 번 실행됨
    bot.loop.create_task(notice_worker(bot, notice_queue))