import asyncio
import aiohttp
import logging
from discord.ext import commands
import discord
from config import LOG_LEVEL, DJANGO_API_URL
from worker import notice_worker

# 로거 (모듈 단위 로깅)
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("bot")

# 필요한 intents 설정
intents = discord.Intents.default()

# 메시지 내용 접근 여부
intents.message_content = True

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

# get 요청 보내기
async def get_data(url, params=None):
    params = params or {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None

# 단일 스터디 일정 출력
@bot.command(name="study_schedule_list")
async def study_schedule_list(ctx, study_id: int):
    guild = ctx.guild
    url = f"{DJANGO_API_URL}studies/{study_id}/discord/study_schedule_list/"
    params = {
        "guild_id": guild.id,
        "guild_name": guild.name,
    }
    study = await get_data(url, params=params)
    if study:
        name = study["name"]
        message = f"## 스터디: { name }\n"
        for schedule in study["schedule"]:
            message += (f"### 제목: {schedule.get('schedule').get('title')}\n"
                        f"- 작성자: {schedule.get('author').get('username')}\n"
                        f"\t- 내용: {schedule.get('schedule').get('description')}\n"
                        f"\t- 시작: {' '.join(schedule.get('schedule').get('start_at')[:-4].split('T'))}\n"
                        f"\t- 종료: {' '.join(schedule.get('schedule').get('end_at')[:-4].split('T'))}\n"
                        )
        await ctx.send(message)
    else:
        await ctx.send("스터디 일정이 존재하지 않습니다.")

# 서버 전체 스터디 일정 출력
@bot.command(name="guild_schedule_list")
async def guild_schedule_list(ctx):
    guild = ctx.guild
    url = f"{DJANGO_API_URL}discord/guild_schedule_list/"
    params = {
        "guild_id": guild.id,
        "guild_name": guild.name,
    }
    data = await get_data(url, params=params)
    if data:
        for study in data:
            name = study["name"]
            message = f"## 스터디: { name }\n"
            for schedule in study["schedule"]:
                message += (f"### 제목: {schedule.get('schedule').get('title')}\n"
                            f"- 작성자: {schedule.get('author').get('username')}\n"
                            f"\t- 내용: {schedule.get('schedule').get('description')}\n"
                            f"\t- 시작: {' '.join(schedule.get('schedule').get('start_at')[:-4].split('T'))}\n"
                            f"\t- 종료: {' '.join(schedule.get('schedule').get('end_at')[:-4].split('T'))}\n"
                            )
            await ctx.send(message)
    else:
        ctx.send("스터디 일정이 존재하지 않습니다.")