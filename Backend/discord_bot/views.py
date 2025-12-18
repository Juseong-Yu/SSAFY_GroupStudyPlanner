from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
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

# @login_required
@api_view(['POST'])
def connect_channel(request, study_id):
    study = get_object_or_404(Study, id=study_id)
    data = request.data
    guild_id = data.get("guild_id")

    guild, _ = DiscordGuild.objects.get_or_create(
        id = guild_id,
        defaults={
            "name": data.get("guild_name"),
            "icon_url": data.get("icon_url"),
            "is_active": True,
        }
    )
    channel, _ = DiscordChannel.objects.get_or_create(
        id = data.get("channel_id"),
        defaults={
            "guild": guild,
            "name": data.get("channel_name"),
            "is_active": True,
        }
    )
    mapping, _ = DiscordStudyMapping.objects.update_or_create(
        study = study,
        defaults = {"channel": channel},
    )
    serializer = DiscordStudyMappingSerializer(mapping)
    return Response(serializer.data, status=status.HTTP_200_OK)

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

import requests
from django.conf import settings

class DiscordOAuthCallbackView(APIView):
    """
    디스코드 OAuth 콜백
    - 디스코드 계정과 웹 계정의 discord_id 일치 여부 검증
    - 사용자가 속한 Guild 목록 반환
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"detail": "Authorization code missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_res = requests.post(
            "https://discord.com/api/oauth2/token",
            data = {
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.DISCORD_REDIRECT_URI,
            },
            headers = {"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_res.status_code != 200:
            return Response({"detail": "Token exchange failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_res.json().get("access_token")

        user_res = request.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        discord_user = user_res.json()
        discord_user_id = discord_user.get("id")

        if str(request.user.discord_id) != str(discord_user_id):
            return Response(
                {"detail": "Discord account mismatch"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        guilds_res = requests.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        return Response({
            "guilds": guilds_res.json()
        })

class DiscordGuildChannelListView(APIView):
    """
    특정 Guild의 채널 목록 조회
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id):
        headers = {
            "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}"
        }

        res = requests.get(
            f"https://discord.com/api/guilds/{guild_id}/channels",
            headers=headers
        )

        if res.status_code != 200:
            return Response({"detail": "Failed to fetch channels"}, status=status.HTTP_400_BAD_REQUEST)
        
        channels = [
            c for c in res.json()
            if c.get("type") == 0
        ]

        return Response(channels)

class ConnectStudyDiscordChannelView(APIView):
    """
    스터디 관리자 디스코드 채널 연동
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, study_id):
        study = get_object_or_404(Study, id=study_id)

        if study.leader != request.user:
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        guild_id = int(request.data.get("guild_id"))
        guild_name = request.data.get("guild_name")
        guild_icon = request.data.get("icon_url")

        channel_id = int(request.data.get("channel_id"))
        channel_name = request.data.get("channel_name")

        guild, _ = DiscordGuild.objects.update_or_crete(
            id = guild_id,
            defaults = {
                "name": guild_name,
                "icon_url": guild_icon,
                "is_active": True,
            }
        )

        channel, _ = DiscordChannel.objects.update_or_create(
            id = channel_id,
            defaults={
                "guild": guild,
                "name": channel_name,
                "is_active": True,
            }
        )

        DiscordStudyMapping.objects.update_or_create(
            study=study,
            defaults={
                "channel": channel
            }
        )

        return Response({"detail": "Discord channel connected successfully"})