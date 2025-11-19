from rest_framework import serializers
from .models import Post, Notice

class NoticeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ('author', 'study', 'created_at', 'updated_at')