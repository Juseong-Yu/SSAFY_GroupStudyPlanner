from fastapi import FastAPI, Header
from pydantic import BaseModel, Field
from typing import Optional
import aiohttp
import logging
from bot import notice_queue  # 전역 큐
from utils import verify_api_key

logger = logging.getLogger("api")
app = FastAPI(title="Discord Bot API")

class NoticeIn(BaseModel):
    channel_id: int
    title: str
    study_id: int
    content: str
    author: str
    url: str | None = None

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


async def get_data(url, params=None):
    params = params or {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None

@app.get("/notice/")
async def receive_notice(payload: NoticeIn):
    item = payload.dict()
    
    await notice_queue.put(item)
    logger.info(f"Received and queued notice: channel={item['channel_id']} title={item['title']}")

    return {"status": "queued", "channel": item['channel_id']}