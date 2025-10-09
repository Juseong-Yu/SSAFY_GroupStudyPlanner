# accounts/views_api.py
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.decorators import method_decorator

from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

# accounts/views_api.py
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})

# 로그인
@require_POST
def login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        auth_login(request, form.get_user())
        return JsonResponse({"detail": "logged in"}, status=200)
    else:
        print(form.errors)
    return JsonResponse(form.errors, status=400)

# 로그아웃 (POST 권장)
@require_POST
def logout(request):
    auth_logout(request)
    return JsonResponse({"detail": "logged out"}, status=200)

# 회원가입
@require_POST
def signup(request):
    form = CustomUserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        # 자동 로그인까지 원하면:
        # auth_login(request, user)
        return JsonResponse(
            {"id": user.id, "email": getattr(user, "email", ""), "username": getattr(user, "username", "")},
            status=201
        )
    return JsonResponse(form.errors, status=400)

# 회원 탈퇴
@require_POST
@login_required
def delete(request):
    request.user.delete()
    return JsonResponse({"detail": "deleted"}, status=200)

# 회원정보 수정
@require_POST
@login_required
def update(request):
    form = CustomUserChangeForm(request.POST or None, instance=request.user)
    if form.is_valid():
        user = form.save()
        return JsonResponse({"detail": "updated"}, status=200)
    return JsonResponse(form.errors, status=400)

# 비밀번호 변경
@require_POST
@login_required
def password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return JsonResponse({"detail": "password changed"}, status=200)
    return JsonResponse(form.errors, status=400)
