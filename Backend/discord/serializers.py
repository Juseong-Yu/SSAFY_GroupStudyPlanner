from rest_framework import serializers
from .models import DiscordGuild, DiscordStudyMapping
from studies.serializers import StudySerializer
from schedules.models import StudySchedule
from schedules.serializers import ScheduleSerializer, UserSerializer

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

class DiscordStudyScheduleSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = StudySchedule
        fields = '__all__'