from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import DiscordGuild, DiscordStudyMapping
from .serializers import DiscordStudyMappingSerializer
from studies.models import Study
from schedules.models import StudySchedule
from schedules.serializers import StudyScheduleSerializer

# Create your views here.

@login_required
@api_view(['POST'])
def connect_study(request, study_id):
    study = get_object_or_404(Study, id=study_id)
    data = request.data
    print(data)
    guild_id = data.get("guild_id")

    guild, _ = DiscordGuild.objects.update_or_create(
        id = guild_id,
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
    mapping = get_object_or_404(DiscordStudyMapping, guild_id=guild_id, study_id=study_id)
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
def guild_schedule_list(request):

    guild_id = request.GET.get("guild_id")
    mappings = DiscordStudyMapping.objects.filter(guild=guild_id)

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
    print(result)
    return Response(result, status=status.HTTP_200_OK)