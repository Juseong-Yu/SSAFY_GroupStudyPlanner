from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 커스텀 클레임 예: username 추가
        token['username'] = user.username
        token['email'] = user.email
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    discord_id = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm", "discord_id")
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 사용자명입니다.")
        return value
    
    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return data
    
    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        discord_id = validated_data.pop("discord_id", None)

        user = User(**validated_data)
        user.set_password(password)

        if discord_id:
            user.discord_id = discord_id

        user.save()
        return user

class PasswordVerifySerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("비밀번호를 입력하세요")
        return value

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 일치하지 않습니다.")
        return value

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "비밀번호가 일치하지 않습니다."})
        # Django의 비밀번호 정책(Validator) 사용
        validate_password(data["new_password"], self.context['request'].user)
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user