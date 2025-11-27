from rest_framework import serializers
from .models import DiscordGuild, DiscordStudyMapping
from studies.serializers import StudySerializer

class DiscordGuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordGuild
        fields = '__all__'


class DiscordStudyMappingSerializer(serializers.ModelSerializer):
    study = StudySerializer(read_only=True)
    guild = DiscordGuildSerializer(read_only=True)

    class Meta:
        model = DiscordStudyMapping
        fields = '__all__'