from typing import Optional, Dict, Any
from fastapi import Header, HTTPException
import logging
import discord
from config import BOT_API_SECRET

logger = logging.getLogger("utils")

def normalize_description(md: str) -> str:
    lines = md.split("\n")
    result = []
    for line in lines:
        if line.strip().startswith("```"):
            result.append(line.strip())
        else:
            result.append(line)
    return "\n".join(result)

def verify_api_key(x_bot_secret: Optional[str]):
    """
    FastAPI 엔드포인트로 들어오는 요청에 대해 간단한 헤더 기반 인증 수행.
    - production에서는 JWT 또는 mTLS 권장.
    """
    if not x_bot_secret or x_bot_secret != BOT_API_SECRET:
        logger.warning("Invalid API key in incoming request")
        raise HTTPException(status_code=401, detail="Unauthorized")

def build_notice_embed(payload: Dict[str, Any]) -> discord.Embed:
    """
    payload에 있는 title/content/author_name로 Embed를 만들어 반환.
    확장 포인트: 필드별 색상, 타임스탬프, 필드 추가 등.
    """
    title = payload.get("title", "공지")
    description = payload.get("content", "")
    url = payload.get("url")
    if url:
        title = f"[{title}]({url})"
    embed = discord.Embed(
        title = None,
        description = (
            f"## {title}\n\n"
            f"{normalize_description(description)}"
        ),
        type = "rich",
        color=0xF1C40F
    )
    
    embed.set_author(name="📢 공지사항")
    embed.timestamp = discord.utils.utcnow()

    # author = payload.get("author")["username"]
    # if author:
    #     embed.set_footer(text=f"작성자: {author}")

    return embed

def build_schedule_embed(payload: Dict[str, Any]) -> discord.Embed:
    """
    payload에 있는 title/content/start_at/end_at로 Embed를 만들어 반환
    """
    title = payload.get("title", "공지")
    description = payload.get("content", "")
    start_at = payload.get("start_at")
    end_at = payload.get("end_at")
    url = payload.get("url")
    if url:
        title = f"[{title}]({url})"

    embed = discord.Embed(
        title=None,
        description = (
            f"## {title}\n\n"
            f"{normalize_description(description)}\n\n"
            f"- 시작: {start_at}\n"
            f"- 종료: {end_at}"
        ),
        type="rich",
        color = 0x3498DB
    )
    embed.set_author(name="🗓️ 신규 일정 생성")
    embed.timestamp = discord.utils.utcnow()
    
    return embed