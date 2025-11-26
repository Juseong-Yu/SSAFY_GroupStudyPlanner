import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

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

if __name__ == "__main__":
    bot.run(TOKEN)