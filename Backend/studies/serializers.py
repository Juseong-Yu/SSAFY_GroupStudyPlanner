from rest_framework import serializers
from .models import Study, StudyMembership

class StudySerializer(serializers.ModelSerializer):

    class Meta:
        model = Study
        fields = '__all__'
        read_only_fields = ('leader', 'members', 'created_at')
