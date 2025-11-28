from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import DiscordGuild, DiscordStudyMapping
from .serializers import DiscordStudyMappingSerializer, DiscordStudyScheduleSerializer
from studies.models import Study
from schedules.models import StudySchedule

# Create your views here.

@login_required
@api_view(['POST'])
def connect_study(request, study_id):
    study = get_object_or_404(Study, id=study_id)
    data = request.data
    guild_id = data["guild_id"]

    guild, _ = DiscordGuild.objects.update_or_create(
        guild_id = guild_id,
        defaults = {
            "id": guild_id,
            "name": data.get("guild_name"),
            "icon_url": data.get("icon_url"),
            "is_active": True,
        }
    )

    mapping, _ = DiscordStudyMapping.objects.update_or_create(
        study = study,
        defaults = {"guild": guild},
    )
    serializer = DiscordStudyMappingSerializer(mapping)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def study_schedule_list(request, study_id):
    
    guild_id = request.query_params.get("guild_id")
    object = get_object_or_404(DiscordStudyMapping, guild_id=guild_id, study_id=study_id)
    schedules = StudySchedule.objects.filter(study=object.study)

    result = []

    for schedule in schedules:
        if schedule.schedule.end_at < timezone.now():
            continue
        result.append(DiscordStudyScheduleSerializer(schedule).data)
    
    result.sort(key=lambda x: x["schedule"]["start_at"])

    return Response(result, status=status.HTTP_200_OK)