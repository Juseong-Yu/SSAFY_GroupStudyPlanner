import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DJANGO_API_URL = os.getenv("DJANGO_API_URL")

intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용이 필요하면 True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    try:
        await bot.tree.sync()  # 슬래시 명령 전체 동기화
        print("Slash commands synced.")
    except Exception as e:
        print("Slash sync failed:", e)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.reply("pong", mention_author=False)

@bot.tree.command(name="hello", description="인사합니다")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"안녕하세요, {interaction.user.display_name}님!")

async def get_study_info(study_id):
    url = f"{DJANGO_API_URL}studies/{study_id}/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()  # JSON 응답 반환
            else:
                return None

@bot.command(name="study")
async def study(ctx, study_id: int):
    """
    !study <id> 명령어 실행 시 해당 스터디 정보 조회
    """
    await ctx.send("스터디 정보를 불러오는 중...")
    data = await get_study_info(study_id)

    if data:
        msg = (f"**스터디 이름:** {data.get('name')}\n"
               f"**리더:** {data.get('leader')}\n"
               )
        await ctx.send(msg)
    else:
        await ctx.send("스터디 정보를 불러오지 못했습니다.")

@bot.command(name="id")
async def id(ctx):
    print(ctx.guild.id)

@bot.command(name="connect")
async def connect(ctx, study_id: int):
    guild = ctx.guild
    icon_url = guild.icon.url if guild.icon else None
    url = f"{DJANGO_API_URL}studies/{study_id}/discord/connect_study/"
    payload = {
        "guild_id": guild.id,
        "guild_name": guild.name,
        "icon_url": icon_url,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = resp.json()
            else:
                data = None
    if data:
        print(data)

@bot.command(name="study_schedule_list")
async def study_schedule_list(ctx, study_id):
    guild = ctx.guild
    url = f"{DJANGO_API_URL}studies/{study_id}/discord/study_schedule_list/"
    params = {
        "guild_id": guild.id,
        "guild_name": guild.name,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                study = await resp.json()
            else:
                study = None
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
        ctx.send("스터디 일정이 존재하지 않습니다.")


@bot.command(name="guild_schedule_list")
async def guild_schedule_list(ctx):
    guild = ctx.guild
    url = f"{DJANGO_API_URL}discord/guild_schedule_list/"
    params = {
        "guild_id": guild.id,
        "guild_name": guild.name,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
            else:
                data = None
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

if __name__ == "__main__":
    bot.run(TOKEN)