from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.decorators import method_decorator
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
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
    
    form = CustomUserChangeForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        
        user = form.save()
        print(form.errors)
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

# 회원정보 조회
def search(request):
    """
    로그인된 사용자의 회원 정보를 반환
    반환 데이터: username, email, profile_img
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)
    user = request.user

    user_data = {
        "username": user.username,
        "email": user.email,
        "profile_img": user.profile_img.url if user.profile_img else None,
    }

    return JsonResponse(user_data, status=200)

@login_required
def check_password(request):
    """
    사용자가 입력한 비밀번호를 확인하고
    맞으면 200 OK, 틀리면 400 반환
    """
    password = request.POST.get('password', '').strip()
    user = request.user

    if not password:
        return JsonResponse({'error': '비밀번호를 입력해주세요.'}, status=400)
    
    # 비밀번호가 맞음
    if user.check_password(password):
        return JsonResponse({'message': 'ok'}, status=200)
    
    # 비밀번호가 틀림
    return JsonResponse({'error': '비밀번호가 올바르지 않습니다.'}, status=400)