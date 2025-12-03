import asyncio
import logging
from typing import Dict
from utils import build_notice_embed, build_schedule_embed
from discord import HTTPException, Forbidden, NotFound
from config import MAX_SEND_RETRIES

logger = logging.getLogger("worker")

async def send_with_retries(channel, embed, max_retries: int = MAX_SEND_RETRIES):
    """
    디스코드 전송 재시도 로직
    - Forbidden/NotFound: 권한이나 채널 문제 -> 재시도하지 않음
    - HTTPException: 일시적 네트워크/서버 문제 -> 재시도
    """
    attempt = 0
    while attempt < max_retries:
        try:
            await channel.send(embed=embed)
            return True
        except Forbidden:
            logger.error("Forbidden to send message to channel %s", getattr(channel, "id", None))
            return False
        except NotFound:
            logger.error("Channel not found: %s", getattr(channel, "id", None))
            return False
        except HTTPException as e:
            attempt += 1
            logger.warning("HTTPException sending message (attempt %d/%d): %s", attempt, max_retries, e)
            await asyncio.sleep(1 * attempt)
    logger.error("Failed to send message after %d attempts", max_retries)
    return False

async def notice_worker(bot, notice_queue: asyncio.Queue):
    """
    무한 루프: 큐에서 항목을 꺼내 채널을 찾고 메시지를 보낸다.
    bot.wait_until_ready()로 봇 준비 완료 후 시작.
    """
    await bot.wait_until_ready()
    logger.info("Notice worker started (bot ready)")

    while True:
        item: Dict = await notice_queue.get()
        try:
            channel_id = int(item["channel_id"])
        except Exception:
            logger.exception("Invalid channel_id in queued item: %s", item)
            notice_queue.task_done()
            continue

        # 캐시 조회
        channel = bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except Exception as e:
                logger.exception(f"Failed to fetch channel {channel_id}: {e}")
                notice_queue.task_done()
                continue

        embed = build_notice_embed(item)

        success = await send_with_retries(channel, embed)
        if success:
            logger.info(f"Sent notice to channel {channel_id}: {item.get('title')}")
        else:
            logger.warning(f"Could not send notice to channel {channel_id}: {item.get('title')}")

        notice_queue.task_done()

async def schedule_worker(bot, schedule_queue: asyncio.Queue):
    await bot.wait_until_ready()
    logger.info("Schedule worker started (bot ready)")

    while True:
        item: Dict = await schedule_queue.get()
        try:
            channel_id = int(item["channel_id"])
        except Exception:
            logger.exception(f"Invalid channel_id in queued item: {item}")
            schedule_queue.task_done()
            continue
    
        channel = bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except Exception as e:
                logger.exception(f"Failed to fetch channel {channel_id}: {e}")
                schedule_queue.task_done()
                continue
        
        embed = build_schedule_embed(item)

        success = await send_with_retries(channel, embed)
        if success:
            logger.info(f"Sent schedule to channel {channel_id}: {item.get('title')}")
        else:
            logger.warning(f"Could not send schedule to channel {channel_id}: {item.get('title')}")