from django.db import models

from studies.models import Study

# Create your models here.

class DiscordGuild(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    icon_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class DiscordChannel(models.Model):
    id = models.BigIntegerField(primary_key=True)
    guild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE, related_name="channels")
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id", "guild"],
                name = "unique_guild_channel_mapping"
            )
        ]


class DiscordStudyMapping(models.Model):
    """
    스터디-디스코드 채널 매핑
    """
    study = models.OneToOneField(Study, primary_key=True, on_delete=models.CASCADE)
    channel = models.ForeignKey(DiscordChannel, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["channel", "study"],
                name = "unique_guild_study_mapping"
            )
        ]