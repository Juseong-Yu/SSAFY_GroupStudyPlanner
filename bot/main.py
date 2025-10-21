import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# intents 설정: 필요한 것만 True로 설정
intents = discord.Intents.default()
intents.message_content = True   # 메시지 내용 읽기 필요 시
intents.members = True           # 멤버 관련 기능 필요 시

bot = commands.Bot(command_prefix="!", intents=intents, help_command=commands.DefaultHelpCommand())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    # 테스트 서버에 명령어 바로 등록(테스트 목적)
    if TEST_GUILD:
        try:
            guild = discord.Object(id=int(TEST_GUILD))
            await bot.tree.sync(guild=guild)
            print("Guild 명령어 동기화 완료")
        except Exception as e:
            print("Guild sync error:", e)
    else:
        # 글로벌 명령어 동기화(전파에 시간이 걸릴 수 있음)
        try:
            await bot.tree.sync()
            print("전역 명령어 동기화 요청 보냄")
        except Exception as e:
            print("Global sync error:", e)

# 텍스트(접두사) 명령 예
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")

# 메시지 이벤트 예
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.lower() == "hello":
        await message.channel.send(f"Hello, {message.author.display_name}!")
    await bot.process_commands(message)  # 반드시 호출

# 슬래시(애플리케이션) 명령 예
@bot.tree.command(name="say", description="입력한 텍스트를 반복합니다")
async def say(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text)

bot.run(TOKEN)