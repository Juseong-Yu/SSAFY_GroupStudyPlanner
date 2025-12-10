import requests
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from .models import Notice
from accounts.models import User
from studies.models import Study
from discord_bot.models import DiscordStudyMapping
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_notice_notification(self, study_id, notice_id):

    try:
        notice = Notice.objects.get(id=notice_id)
        study = Study.objects.get(id=study_id)
    except:
        logger.warning(f"send_notice_notification: notice {notice_id} does not exist")
    
    mapping = DiscordStudyMapping.objects.filter(study=study_id).first()
    if not mapping:
        logger.info(f"send_notice_notification: no discord mapping for notice {notice_id}")
        return
    print(notice.author)
    payload = {
                    "channel_id": mapping.channel.id,
                    "study_name": study.name,
                    "title": notice.title,
                    "content": notice.content,
                    "author": notice.author.username,
                    "url": f"{settings.VUE_API_URL}studies/{study_id}/notice/{notice.id}"
                }
    
    url = f"{settings.DISCORD_WEBHOOK_URL}notice/"

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"send_notice_notification: sent notice {notice_id} to discord")
        else:
            logger.warning(f"send_notice_notification: non-200 status {response.status_code} for notice {notice_id}")
            raise Exception(f"discord returneds status {response.status_code}")
    except requests.RequestException as exc:
        try:
            logger.exception(f"send_notice_notification: request exception, will retry: {exc}")
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"send_notice_notification: max retries exceeded for notice {notice_id}")
    except Exception as exc:
        logger.exception(f"send_notice_notification: unexpected error for notice {notice_id}: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"send_notice_notification: max retries exceeded (unexpected) for notice {notice_id}")