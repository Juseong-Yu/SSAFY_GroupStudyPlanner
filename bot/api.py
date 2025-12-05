from fastapi import FastAPI, Header
from pydantic import BaseModel, Field
from typing import Optional
import logging
from bot import notice_queue, new_schedule_queue, remind_schedule_queue  # 전역 큐
from utils import verify_api_key

logger = logging.getLogger("api")
app = FastAPI(title="Discord Bot API")

class NoticeIn(BaseModel):
    channel_id: int
    study_name: str
    title: str
    content: str
    author: str
    url: str | None = None

class ScheduleIn(BaseModel):
    channel_id: int
    study_name: str
    title: str
    content: str
    start_at: str
    end_at: str
    url: str | None = None

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/notice/")
async def receive_notice(payload: NoticeIn):
    item = payload.dict()
    
    await notice_queue.put(item)
    logger.info(f"Received and queued notice: channel={item['channel_id']} title={item['title']}")

    return {"status": "queued", "channel": item['channel_id']}

@app.post("/new_schedule/")
async def receive_schedule(payload: ScheduleIn):
    item = payload.dict()

    await new_schedule_queue.put(item)
    logger.info(f"Received and queued schedule: channel={item['channel_id']} title={item['title']}")

    return {"status": "queued", "channel": item['channel_id']}

@app.post("/remind_schedule/")
async def remind_schedule(payload: ScheduleIn):
    item = payload.dict()

    await remind_schedule_queue.put(item)
    logger.info(f"Received and queued schedule: channel={item['channel_id']} title={item['title']}")

    return {"status": "queued", "channel": item['channel_id']}