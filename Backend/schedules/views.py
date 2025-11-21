from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Schedule, StudySchedule, PersonalSchedule
from studies.models import Study, StudyMembership
from .serializers import ScheduleSerializer, StudyScheduleSerializer, PersonalSchedulesSerializer

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

