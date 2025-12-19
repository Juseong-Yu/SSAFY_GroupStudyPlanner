from rest_framework import serializers
from .models import Study, StudyMembership
from accounts.models import User

class StudySerializer(serializers.ModelSerializer):

    class Meta:
        model = Study
        fields = ('id', 'name', 'leader', 'created_at')
        read_only_fields = ('leader', 'created_at')

class StudyMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'
        read_only_fields = ('leader', 'members', 'created_at')

class StudyMembershipSerializer(serializers.ModelSerializer):
    # Study 모델의 id와 name을 포함하도록 설정
    id = serializers.IntegerField(source='study.id', read_only=True)
    name = serializers.CharField(source='study.name', read_only=True)
    leader = serializers.CharField(source='study.leader.username', read_only=True)  # 리더 정보 (username만)
    created_at = serializers.DateTimeField(source='study.created_at', format="%Y-%m-%d %H:%M:%S", read_only=True)
    joined_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = StudyMembership
        fields = ('id', 'name', 'leader', 'role', 'is_active', 'joined_at', 'created_at')

class UserSerializer(serializers.ModelSerializer):
    """
    앱에서 필요한 사용자 정보
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class StudyRoleSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    study = StudySerializer(read_only=True)

    class Meta:
        model = StudyMembership
        fields = ('user', 'study', 'role')

class RoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = StudyMembership
        fields = ('user', 'role')