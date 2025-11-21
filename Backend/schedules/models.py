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