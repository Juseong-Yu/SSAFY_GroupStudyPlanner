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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, PasswordVerifySerializer, PasswordChangeSerializer

import urllib.parse

from django.conf import settings

@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})

# 회원가입
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "profile_img": request.build_absolute_uri(user.profile_img.url) if user.profile_img else None
        }, status=status.HTTP_201_CREATED)

# 회원정보 수정
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update(request):
    form = CustomUserChangeForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        user = form.save()
        return JsonResponse({"detail": "updated"}, status=200)
    return JsonResponse(form.errors, status=400)

# 비밀번호 변경
api_view(['PUT'])
@permission_classes([IsAuthenticated])
def password_change(request):
    serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # JWT: 비밀번호 변경 후 기존 토큰(특히 refresh token)을 무력화하려면 블랙리스트/토큰 회전 필요
    return Response({"detail": "비밀번호가 변경되었습니다."}, status=status.HTTP_200_OK)

@require_POST
@permission_classes([IsAuthenticated])
def password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return JsonResponse({"detail": "password changed"}, status=200)
    return JsonResponse(form.errors, status=400)

# 회원정보 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search(request):
    """
    로그인된 사용자의 회원 정보를 반환
    반환 데이터: username, email, profile_img
    """
    user = request.user
    user_data = {
        "username": user.username,
        "email": user.email,
        "profile_img": user.profile_img.url if user.profile_img else None,
    }

    return JsonResponse(user_data, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_password(request):
    serializer = PasswordVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    password = serializer.validated_data['password']
    is_valid = request.user.check_password(password)

    return Response({"valid": is_valid}, status=status.HTTP_200_OK)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # token_blacklist 앱이 활성화되어 있어야 함
        except Exception as e:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"detail": "ok"})
    
import os
import requests
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class DiscordCallbackView(APIView):
    """
    **Discord OAuth Callback 처리**
    프론트가 Discord authorization_code를 POST로 전달하면,
    서버는 아래 단계를 수행한다.

    1. Discord OAuth Token 교환
    2. Access Token으로 사용자 정보 조회
    3. DB에서 기존 사용자 조회 또는 신규 생성
    4. JWT(access, refresh) 발급 후 반환
    """

    def post(self, request):
        # -----------------------------------------------------------
        # 0) 프론트에서 code가 전달되지 않은 경우
        # -----------------------------------------------------------
        code = request.data.get('code')
        if not code:
            return Response(
                {'detail': 'Code not provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------------
        # 1) Discord OAuth2 Token 교환
        # -----------------------------------------------------------
        token_url = "https://discord.com/api/oauth2/token"

        data = {
            "client_id": os.environ.get('DISCORD_CLIENT_ID'),
            "client_secret": os.environ.get('DISCORD_CLIENT_SECRET'),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.environ.get('DISCORD_REDIRECT_URI'),  # 반드시 동일해야 함
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        token_resp = requests.post(token_url, data=data, headers=headers)

        if token_resp.status_code != 200:
            return Response(
                {'detail': 'Token exchange failed', 'discord_response': token_resp.text},
                status=status.HTTP_400_BAD_REQUEST
            )

        token_json = token_resp.json()
        access_token = token_json.get('access_token')

        if not access_token:
            return Response(
                {'detail': 'No access token returned'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------------
        # 2) Discord 사용자 정보 조회
        # -----------------------------------------------------------
        user_info_url = "https://discord.com/api/users/@me"
        user_info_resp = requests.get(
            user_info_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if user_info_resp.status_code != 200:
            return Response(
                {'detail': 'Failed to fetch user info', 'discord_response': user_info_resp.text},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_info = user_info_resp.json()
        # 예: {'id': '123', 'username': 'tester', 'avatar': 'xxxx', 'email': null }

        discord_id = user_info.get('id')
        username = user_info.get('username')
        email = user_info.get('email')  # email은 scope에 따라 null일 수 있음

        # -----------------------------------------------------------
        # 2-1) 이메일이 없는 경우 처리
        # 서버 정책: "email이 필요할 수 있음" → 기본값: email 필요!
        # -----------------------------------------------------------
        if not email:
            return Response(
                {'detail': 'Discord did not return email. Email scope must be enabled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------------------------
        # 3) 기존 사용자 조회 또는 신규 생성
        # -----------------------------------------------------------
        try:
            user = User.objects.get(email=email)

            # 기존 사용자라면 원하는 정책대로 디스코드 ID 저장, 업데이트 가능
            # 예: user.discord_id = discord_id
            #     user.save()

        except User.DoesNotExist:
            # 신규 생성
            user = User.objects.create(
                username=username,
                email=email
            )
            user.set_unusable_password()
            user.save()

        # -----------------------------------------------------------
        # 4) JWT 발급
        # -----------------------------------------------------------
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'discord_id': discord_id,
            'email': email,
            'username': username,
        })

DISCORD_CLIENT_ID = settings.DISCORD_CLIENT_ID
DISCORD_CLIENT_SECRET = settings.DISCORD_CLIENT_SECRET
DISCORD_REDIRECT_URI = settings.DISCORD_REDIRECT_URI
DISCORD_REDIRECT_URI_FOR_LOGIN = settings.DISCORD_REDIRECT_URI_FOR_LOGIN
DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def connect_discord(request):
    """
    디스코드 연동 시작
    """
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify email"
    }
    url = f"{DISCORD_OAUTH_URL}?{urllib.parse.urlencode(params)}"
    return Response({"auth_url": url})

@api_view(['GET'])
@permission_classes([AllowAny])
def discord_callback(request):
    """
    디스코드 콜백에서 사용자 계정과 연결
    """
    code = request.query_params.get("code")
    if not code:
        return Response({"error": "Code missing"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 1. 토큰 교환
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }

    token_res = requests.post(
        DISCORD_TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if token_res.status_code != 200:
        return Response(
            {"detail": "Token exchange failed", "discord_response": token_res.text},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    token_json = token_res.json()
    access_token = token_json.get("access_token")
    refresh_token = token_json.get("refresh_token")

    # 2. Discord 유저 정보 조회
    user_res = requests.get(
        DISCORD_USER_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if user_res.status_code != 200:
        return Response(
            {"detail": "Failed to fetch Discord user", "discord_response": user_res.text},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    discord_user = user_res.json()

    if "id" not in discord_user:
        return Response(
            {"detail": "Invalid Discord user response", "discord_response": discord_user},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 3. 현재 로그인한 계정과 연결
    if not request.user.is_authenticated:
        return Response(
            {"detail": "User must be logged in to link Discord"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    
    user = request.user
    user.discord_id = discord_user["id"]
    user.discord_refresh_token = refresh_token
    user.save()

    return Response({"detail": "Discord successfully connected"})

@api_view(['GET'])
def login_with_discord(request):
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_url": DISCORD_REDIRECT_URI_FOR_LOGIN,
        "response_type": "code",
        "scope": "identify email"
    }
    url = f"{DISCORD_OAUTH_URL}?{urllib.parse.urlencode(params)}"
    return Response({"auth_url": url})

@api_view(['GET'])
def discord_login_callback(request):
    """
    Discord 로그인용 callback.
    - Discord가 redirect (GET) 으로 보내온 ?code= 을 수신.
    - code -> 토큰 교환 -> /users/@me 로 사용자 정보 조회.
    - 조회한 discord_id 로 이미 연동된 User를 찾음.
    - 존재하면 JWT(access, refresh) 발급하여 반환.
    - 연동된 사용자가 없으면 400 (연동 필요).
    """
    code = request.GET.get("code")
    if not code:
        return Response({"detail": "code query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    # 1) 토큰 교환: authorization_code -> access_token
    #    반드시 redirect_uri가 Discord 개발자 포털에 등록된 값과 동일해야 함
    token_data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }

    # x-www-form-urlencoded 로 전송
    try:
        token_resp = requests.post(DISCORD_TOKEN_URL, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10)
    except requests.RequestException as e:
        return Response({'detail': 'Failed to reach Discord token endpoint', 'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    if token_resp.status_code != 200:
        # Discord가 반환한 에러 메시지 포함
        return Response({'detail': 'Token exchange failed', 'discord_response': token_resp.text}, status=status.HTTP_400_BAD_REQUEST)

    token_json = token_resp.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return Response({'detail': 'No access token returned by Discord', 'discord_response': token_json}, status=status.HTTP_400_BAD_REQUEST)
    
    # 2) 사용자 정보 조회 (/users/@me)
    try:
        user_info_resp = requests.get(DISCORD_USER_URL, headers={'Authorization': f'Bearer {access_token}'}, timeout=10)
    except requests.RequestException as e:
        return Response({'detail': 'Failed to reach Discord user endpoint', 'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    if user_info_resp.status_code != 200:
        return Response({'detail': 'Failed to fetch user info from Discord', 'discord_response': user_info_resp.text}, status=status.HTTP_400_BAD_REQUEST)

    # discord_user 예시: { "id": "123", "username": "name", "discriminator": "0001", "email": "user@example.com", ... }
    discord_user = user_info_resp.json()

    discord_id = discord_user.get('id')
    if not discord_id:
        return Response({'detail': 'Discord response missing user id', 'discord_response': discord_user}, status=status.HTTP_400_BAD_REQUEST)

    # 3) 이미 연동된 계정 찾기: discord_id 로 User 검색
    try:
        user = User.objects.get(discord_id=discord_id)
    except User.DoesNotExist:
        # 연동된 계정이 없으면 클라이언트가 계정 연동을 유도하도록 400 반환
        return Response({'detail': 'No linked account for this Discord user. Link Discord in account settings first.'}, status=status.HTTP_400_BAD_REQUEST)

    # 4) JWT 발급 (SimpleJWT 사용)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.pk,
            'email': user.email,
            'username': getattr(user, 'username', None),
        }
    })