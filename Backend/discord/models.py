from django.db import models

from studies.models import Study

# Create your models here.

class DiscordGuild(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    icon_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class DiscordStudyMapping(models.Model):
    """
    스터디-디스코드 서버 매핑
    """
    study = models.OneToOneField(Study, primary_key=True, on_delete=models.CASCADE)
    guild = models.ForeignKey(DiscordGuild, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["guild", "study"],
                name = "unique_guild_study_mapping"
            )
        ]