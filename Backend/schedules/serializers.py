from rest_framework import serializers
from .models import Schedule, StudySchedule, PersonalSchedule
from accounts.models import User
from studies.models import Study

class UserSerializer(serializers.ModelSerializer):
    """
    schedules 앱에서 필요한 사용자 정보
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_img')

class ScheduleSerializer(serializers.ModelSerializer):
    """
    기본 일정 정보
    StudySchedule / PersonalSchedule에서 공통으로 사용
    """
    class Meta:
        model = Schedule
        fields = ('id', 'title', 'description', 'start_at', 'end_at')

class StudySerializer(serializers.ModelSerializer):
    """
    스터디 일정에서 필요한 스터디 정보
    """
    class Meta:
        model = Study
        fields = ('id', 'name')

class StudyScheduleSerializer(serializers.ModelSerializer):
    """
    스터디 일정 정보
    """
    schedule = ScheduleSerializer(read_only=True)
    author = UserSerializer(read_only=True)
    study = StudySerializer(read_only=True)
    class Meta:
        model = StudySchedule
        fields = '__all__'

class PersonalSchedulesSerializer(serializers.ModelSerializer):
    """
    개인 일정 정보
    """
    schedule = ScheduleSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = PersonalSchedule
        fields = '__all__'