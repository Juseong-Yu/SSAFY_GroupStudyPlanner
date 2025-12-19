from rest_framework import serializers
from .models import DiscordGuild, DiscordChannel, DiscordStudyMapping
from studies.serializers import StudySerializer

class DiscordGuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordGuild
        fields = '__all__'

class DiscordChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordChannel
        fields = '__all__'

class DiscordStudyMappingSerializer(serializers.ModelSerializer):
    study = StudySerializer(read_only=True)
    guild = DiscordGuildSerializer(read_only=True)
    channel = DiscordChannelSerializer(read_only=True)

    guild_id = serializers.CharField(read_only=True)
    channel_id = serializers.CharField(read_only=True)

    class Meta:
        model = DiscordStudyMapping
        fields = ('study', 'guild', 'channel', 'guild_id', 'channel_id')