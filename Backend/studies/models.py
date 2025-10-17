from django.db import models
from django.conf import settings

# Create your models here.
class Study(models.Model):
    name = models.CharField(max_length=40)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through = 'StudyMembership',
        related_name='joined_studies'
    ),
    created_at = models.DateTimeField(auto_now_add=True)

class StudyMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices = [('leader', '리더'), ('admin', '관리자'), ('member', '그룹원')],
        default = 'member'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'study')