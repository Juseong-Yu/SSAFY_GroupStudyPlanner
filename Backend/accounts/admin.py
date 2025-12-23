from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
# admin.site.register(User, UserAdmin)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. 필드셋 설정 (기존 UserAdmin 설정을 가져오되 커스텀 필드 추가)
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('profile_img', 'discord_id', 'discord_refresh_token', )}),
    )

    # 2. 읽기 전용 필드 설정 (핵심: date_joined를 여기에 추가)
    readonly_fields = ('date_joined', 'last_login')

    ordering = ('email',)