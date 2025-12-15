import requests
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from .models import Reminder, Schedule
from studies.models import Study
from discord_bot.models import DiscordStudyMapping
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_schedule_notification(self, study_id, schedule_id):
    """
    스케줄 생성 후 디스코드로 새 스케줄 알림을 전송하는 작업.
    실패 시 재시도. idempotency 처리를 위해 DB에서 이미 전송되었는지 확인하도록 확장 가능.
    """
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        study = Study.objects.get(id=study_id)
    except Schedule.DoesNotExist:
        logger.warning(f"send_schedule_notification: schedule {schedule_id} does not exist")
        return

    mapping = DiscordStudyMapping.objects.filter(study=study_id).first()
    if not mapping:
        logger.info(f"send_schedule_notification: no discord mapping for schedule {schedule_id}")
        return

    payload = {
        "channel_id": mapping.channel.id if getattr(mapping, "channel", None) else None,
        "study_name": study.name,
        "title": schedule.title,
        "content": schedule.description,
        "start_at": schedule.start_at.isoformat() if schedule.start_at else None,
        "end_at": schedule.end_at.isoformat() if schedule.end_at else None,
        "url": f"{settings.VUE_API_URL}studies/{study_id}/schedule/"
    }

    url = f"{settings.DISCORD_WEBHOOK_URL}new_schedule/"

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"send_schedule_notification: sent schedule {schedule_id} to discord")
        else:
            logger.warning(f"send_schedule_notification: non-200 status {response.status_code} for schedule {schedule_id}")
            raise Exception(f"discord returneds status {response.status_code}")
    except requests.RequestException as exc:
        try:
            logger.exception(f"send_schedule_notification: request exception, will retry: {exc}")
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"send_schedule_notification: max retries exceeded for schedule {schedule_id}")
    except Exception as exc:
        logger.exception(f"send_schedule_notification: unexpected error for schedule {schedule_id}: {exc}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"send_schedule_notification: max retries exceeded (unexpected) for schedule {schedule_id}")

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_reminder(self, reminder_id):
    """
    개별 Reminder 전송 작업.
    외부 API 호출을 담당함.
    - Discord API 오류 → 자동 재시도
    - 네트워크 오류 → 자동 재시도
    - Reminder 객체 없음 → 즉시 종료
    - 응답 200 OK 시 sent=True 처리
    """
    try:
        try:
            reminder = Reminder.objects.get(id=reminder_id)
        except Reminder.DoesNotExist:
            return

        if reminder.sent:
            return
        
        payload = reminder.payload
        url = f"{settings.DISCORD_WEBHOOK_URL}remind_schedule/"

        try:
            response = requests.post(url, json=payload, timeout=5)
        except requests.RequestException as exc:
            raise self.retry(exc=exc)

        if response.status_code == 200:
            reminder.sent = True
            reminder.save()
            return
        
        raise self.retry(
            exc=Exception(f"Bad response: {response.status_code}")
        )

    except self.MaxRetriesExccededError:
        return

@shared_task
def scan_and_send_reminders():
    """
    Celery Beat가 매 분마다 실행하는 작업
    전송 시각이 지난 Reminder들 조회 후 send_reminder 작업 큐에 전달
    """
    now = timezone.now()

    due_list = Reminder.objects.filter(sent=False, sent_time__lte=now)

    for r in due_list:
        send_reminder.delay(r.id)