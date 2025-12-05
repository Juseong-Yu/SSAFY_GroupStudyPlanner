import requests
from django.utils import timezone
from celery import shared_task
from .models import Reminder

from django.conf import settings

@shared_task
def send_reminder(reminder_id):
    """
    개별 Reminder 전송 작업.
    외부 API 호출을 담당함.
    """
    try:
        reminder = Reminder.objects.get(id=reminder_id)

        if reminder.sent:
            return
        
        payload = reminder.payload
        url = f"{settings.DISCORD_WEBHOOK_URL}remind_schedule/"

        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            reminder.sent = True
            reminder.save()

    except Reminder.DoesNotExist:
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