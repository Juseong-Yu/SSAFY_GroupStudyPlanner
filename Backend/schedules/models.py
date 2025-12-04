from django.db import models
from django.conf import settings

# Create your models here.

class Schedule(models.Model):
    """
    기본 일정 정보
    스터디, 개인 무관하게 일정에 관한 공통 필드를 담음
    """
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 이 일정에 대한 리마인더가 있는지 여부
    has_reminders = models.BooleanField(default=False)

class Reminder(models.Model):
    """
    개별 리마인더 항목
    - schedule: 어떤 일정에 대한 리마인더인지
    - offset: start_at(또는 end_at) 대비 얼마나 빨리 알릴지 (예: 1일 전 = timedelta(days=1))
              offset이 비어있으면 send_at을 직접 쓸 수 있음.
    - payload: 알림에 필요한 추가 정보(예: guild_id, channel_id 등) (JSON)
    - sent: 이미 전송되었는지 플래그
    """
    schedule = models.ForeignKey(Schedule, related_name="reminders", on_delete=models.CASCADE)
    # offset을 주로 사용: 일정 시작 기준으로 얼마만큼 이전에 보낼지
    offset = models.IntegerField()
    sent_time = models.DateTimeField()

    payload = models.JSONField(default=dict, blank=True)
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class StudySchedule(models.Model):
    """
    스터디에 소속된 일정
    """
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    study = models.ForeignKey("studies.Study", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class PersonalSchedule(models.Model):
    """
    개인이 등록하는 일정
    """
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)