from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Schedule, StudySchedule, PersonalSchedule
from studies.models import Study, StudyMembership
from .serializers import ScheduleSerializer, StudyScheduleSerializer, PersonalScheduleSerializer
from discord.models import DiscordStudyMapping

from django.conf import settings
import requests

# Create your views here.

NOT_MEMBER = "NOT_MEMBER"
NOT_AUTHORIZED = "NOT_AUTHORIZED"

def error_list(code):
    if code == "NOT_MEMBER":
        return Response({"error": "스터디 멤버가 아닙니다."},
                        status=status.HTTP_403_FORBIDDEN,
                        json_dumps_params={"ensure_ascii": False})
    elif code == 'NOT_AUTHORIZED':
        return Response({"error": "권한이 없습니다."},
                        status=status.HTTP_403_FORBIDDEN,
                        json_dumps_params={"ensure_ascii": False})

@login_required
@api_view(['POST'])
def study_schedule_create(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id = study_id)
    
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    if membership.role not in ('leader', 'admin'):
            return error_list(NOT_AUTHORIZED)
    
    # schedule 생성
    schedule_serializer = ScheduleSerializer(data = request.data)
    schedule_serializer.is_valid(raise_exception=True)
    schedule = schedule_serializer.save()

    # 디스코드 알림
    mapping = DiscordStudyMapping.objects.get(study=study_id)
    if mapping:
        url = f"{settings.DISCORD_WEBHOOK_URL}schedule/"

        payload = {
            "channel_id": mapping.channel.id,
            "study_id": study_id,
            "title": schedule_serializer.data["title"],
            "content": schedule_serializer.data["description"],
            "start_at": schedule_serializer.data["start_at"],
            "end_at": schedule_serializer.data["end_at"],
            "url": f"{settings.VUE_API_URL}studies/{study_id}/schedule/"
        }
        try:
            requests.post(url, json=payload)
        except:
            pass

    # study schedule 생성
    study_schedule = StudySchedule.objects.create(
        schedule = schedule,
        study = study,
        author = user,
    )
    return Response(StudyScheduleSerializer(study_schedule).data, status=status.HTTP_201_CREATED)

@login_required
@api_view(['GET'])
def study_schedule_list(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id = study_id)

    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    schedules = StudySchedule.objects.filter(study_id=study_id)
    return Response(StudyScheduleSerializer(schedules, many=True).data, status=status.HTTP_200_OK)

@login_required
@api_view(['GET', 'PUT', 'DELETE'])
def study_schedule_detail(request, study_id, schedule_id):

    user = request.user
    study = get_object_or_404(Study, id = study_id)

    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    study_schedule = get_object_or_404(StudySchedule, id=schedule_id)
    schedule = study_schedule.schedule

    # 단일 일정 조회
    if request.method == 'GET':
        serializer = StudyScheduleSerializer(study_schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 일정 수정
    elif request.method == 'PUT':
        if membership.role not in ('leader', 'admin'):
            return error_list(NOT_AUTHORIZED)
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 일정 삭제
    elif request.method == 'DELETE':
        if membership.role not in ('leader', 'admin'):
            return error_list(NOT_AUTHORIZED)
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
@api_view(['POST'])
def personal_schedule_create(request):
    user = request.user

    schedule_serializer = ScheduleSerializer(data = request.data)
    schedule_serializer.is_valid(raise_exception = True)
    schedule = schedule_serializer.save()

    personal_schedule = PersonalSchedule.objects.create(
        schedule = schedule,
        user = user,
    )
    return Response(PersonalScheduleSerializer(personal_schedule).data, status=status.HTTP_201_CREATED)

@login_required
@api_view(['GET'])
def personal_schedule_list(request):
    user = request.user

    schedules = PersonalSchedule.objects.filter(user = user)
    return Response(PersonalScheduleSerializer(schedules, many=True).data, status=status.HTTP_200_OK)

@login_required
@api_view(['GET', 'PUT', 'DELETE'])
def personal_schedule_detail(request, schedule_id):
    user = request.user

    personal_schedule = get_object_or_404(PersonalSchedule, id=schedule_id)
    schedule = personal_schedule.schedule

    # 본인 확인
    if personal_schedule.user != user:
        return error_list(NOT_AUTHORIZED)

    # 개인 일정 확인
    if request.method == 'GET':
        serializer = PersonalScheduleSerializer(personal_schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 개인 일정 수정
    elif request.method == 'PUT':
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 개인 일정 삭제
    elif request.method == 'DELETE':
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
@api_view(['GET'])
def schedule_list(request):
    user = request.user

    study_ids = user.study_membership.filter(is_active=True).values_list('study_id', flat=True)
    study_schedules = StudySchedule.objects.filter(study_id__in=study_ids)
    personal_schedules = PersonalSchedule.objects.filter(user=user)

    result = []

    for ss in study_schedules:
        result.append({
            "type": "study",
            "data": StudyScheduleSerializer(ss).data
        })
    
    for ps in personal_schedules:
        result.append({
            "type": "personal",
            "data": PersonalScheduleSerializer(ps).data
        })
    
    result.sort(key=lambda x: x["data"]["schedule"]["start_at"])

    return Response(result, status=status.HTTP_200_OK)