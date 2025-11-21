from rest_framework import serializers
from .models import Post, Notice
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_img')

class NoticeSerializer(serializers.ModelSerializer):
    
    author = UserSerializer(read_only=True)

    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ('author', 'study', 'created_at', 'updated_at')

class NoticeListSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)

    class Meta:
        model = Notice
        fields = ('id', 'title', 'created_at', 'updated_at', 'study_id', 'author')