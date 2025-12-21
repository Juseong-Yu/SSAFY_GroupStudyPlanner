from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView


from .models import DiscordGuild, DiscordChannel, DiscordStudyMapping
from .serializers import DiscordStudyMappingSerializer
from studies.models import Study
from schedules.models import StudySchedule
from schedules.serializers import StudyScheduleSerializer

# Create your views here.

@api_view(['GET'])
def study_schedule_list(request, study_id):
    channel_id = request.query_params.get("channel_id")
    mapping = get_object_or_404(DiscordStudyMapping, channel_id=channel_id, study_id=study_id)
    study = Study.objects.get(id=study_id)
    schedules = StudySchedule.objects.filter(study=study)

    result = {"id": study.id,
               "name": study.name,
               "schedule": []}

    for schedule in schedules:
        if schedule.schedule.end_at < timezone.now():
            continue
        result["schedule"].append(StudyScheduleSerializer(schedule).data)
    
    result["schedule"].sort(key=lambda x: x["schedule"]["start_at"])

    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET'])
def channel_schedule_list(request):

    channel_id = request.GET.get("channel_id")
    mappings = DiscordStudyMapping.objects.filter(channel_id=channel_id)

    if not mappings:
        return Response(status=status.HTTP_404_NOT_FOUND)

    result = []
    for mapping in mappings:
        schedules = StudySchedule.objects.filter(study=mapping.study)
        study = Study.objects.get(id=mapping.study.id)
        res = {"id": study.id,
               "name": study.name,
               "schedule": []}
        for schedule in schedules:
            if schedule.schedule.end_at < timezone.now():
                continue
            res["schedule"].append(StudyScheduleSerializer(schedule).data)
        result.append(res)
    return Response(result, status=status.HTTP_200_OK)

from django.conf import settings
from urllib.parse import urlencode
import requests

class DiscordBotInviteView(APIView):
    """
    Discord 봇 초대 OAuth URL 반환
    """
    def get(self, request, study_id):
        params = {
            "client_id": settings.DISCORD_CLIENT_ID,
            "redirect_uri": settings.DISCORD_REDIRECT_URI_CONNECT_STUDY,
            # "redirect_uri": "http://localhost:8000/studies/1/discord/bot/callback/",
            "response_type": "code",
            "scope": "bot",
            "permissions": settings.DISCORD_PERMISSIONS,
        }

        url = f"{settings.DISCORD_OAUTH_URL}?{urlencode(params)}"
        return Response({"url": url})

class DiscordBotCallbackView(APIView):
    """
    봇 초대 완료 후 callback
    - guild_id는 query parameter로 전달됨
    """

    def get(self, request, study_id):
        guild_id = request.query_params.get("guild_id") 
        if not guild_id:
            return Response({"detail": "guild_id가 전달되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 서버 정보 조회
        guild_res = requests.get(
            f"https://discord.com/api/guilds/{guild_id}",
            headers = {
                "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}"
            }
        )

        if guild_res.status_code != 200:
            return Response(
                {"detail": "Bot is not invited or lacks permission"},
                status=status.HTTP_400_BAD_REQUEST
            )


        guild_data = guild_res.json()
        icon = guild_data.get("icon")
        icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{icon}.png" if icon else None

        guild, _ = DiscordGuild.objects.update_or_create(
            id = guild_id,
            defaults = {
                "name": guild_data.get("name"),
                "icon_url": icon_url,
                "is_active": True,
            }
        )
        
        study = get_object_or_404(Study, id=study_id)
        mapping, _ = DiscordStudyMapping.objects.update_or_create(
            study=study,
            defaults={
                "guild": guild,
                "channel": None
            }
        )

        return Response({"detail": "successfully invited"}, status=status.HTTP_200_OK)

class FetchGuildChannel(APIView):
    """
    봇이 초대된 서버의 채널 목록 조회
    """
    def get(self, request, study_id, guild_id):
        channel_res = requests.get(
            f"https://discord.com/api/guilds/{guild_id}/channels",
            headers = {
                "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}"
            }
        )
        if channel_res.status_code != 200:
            return Response(
                {"detail": "Failed to fetch channels"},
                status=status.HTTP_400_BAD_REQUEST
            )

        guild = get_object_or_404(DiscordGuild, id=guild_id)
        mapping = get_object_or_404(
            DiscordStudyMapping,
            study_id=study_id,
            guild=guild
        )

        channel_list = []
        for ch in channel_res.json():
            if ch["type"] == 0:
                channel, _ = DiscordChannel.objects.update_or_create(
                    id = ch["id"],
                    guild=guild,
                    defaults = {
                        "name": ch.get("name"),
                        "is_active": True,
                    }
                )
                channel_list.append({
                    "id": str(channel.id),
                    "name": channel.name,
                })
        
        return Response({
            "guild": {
                "id": str(guild.id),
                "name": guild.name,
            },
            "channels": channel_list,
        })

class DiscordStudyChannelConnectView(APIView):
    """
    선택한 Discord 채널을 스터디와 연결
    """

    def post(self, request, study_id):
        channel_id = request.data.get("channel_id")

        if not channel_id:
            return Response({"detail": "channel_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        study = Study.objects.get(id=study_id)
        channel = DiscordChannel.objects.get(id=channel_id)

        DiscordStudyMapping.objects.update_or_create(
            study = study,
            defaults = {
                "channel": channel
            }
        )

        return Response({
            "detail": "successfully connected"
        }, status=status.HTTP_200_OK)

class GetConnectedDiscordGuild(APIView):
    """
    스터디에 연결된 Discord 서버 정보 조회
    """

    def get(self, request, study_id):
        mapping = get_object_or_404(DiscordStudyMapping, study_id=study_id)
        if not mapping.guild:
            return Response({"detail": "No guild connected"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DiscordStudyMappingSerializer(mapping)
        return Response(serializer.data, status=status.HTTP_200_OK)