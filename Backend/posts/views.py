from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import Notice, Post, UploadedImage
from studies.models import Study, StudyMembership
from .serializers import NoticeSerializer, NoticeListSerializer, UploadedImageSerializer
from discord.models import DiscordStudyMapping

from django.conf import settings

# Create your views here.

NOT_MEMBER = "NOT_MEMBER"
NOT_AUTHORIZED = "NOT_AUTHORIZED"

def error_list(code):
    if code == "NOT_MEMBER":
        return Response({"error": "스터디 멤버가 아닙니다."},
                        status=status.HTTP_403_FORBIDDEN,
                        json_dumps_params={"ensure_ascii": False})
    elif code == 'NOT_AUTHORIZED':
        return Response({"error": "권한이 없습니다."},
                        status=status.HTTP_403_FORBIDDEN,
                        json_dumps_params={"ensure_ascii": False})

@login_required
@api_view(['POST'])
def notice_create(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)

    # 공자사항 작성
    if request.method == 'POST':
        if membership.role not in ('leader', 'admin'):
            return error_list(NOT_AUTHORIZED)

        serializer = NoticeSerializer(data=request.data)
        if serializer.is_valid():

            notice = serializer.save(author = request.user, study = study)
            channel = DiscordStudyMapping.objects.get(study=study_id)
            if channel:
                url = f"{settings.DISCORD_WEBHOOK_URL}notice/"
                import requests
                payload = {
                    "channel_id": channel.guild.id,
                    "study_id": study_id,
                    "title": serializer.data["title"],
                    "content": serializer.data["content"],
                    "author": user.username,
                    "url": f"{settings.VUE_API_URL}studies/{study_id}/posts/notice_detail/{notice.id}"
                }
                requests.post(url, json=payload)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['GET', 'PUT', 'DELETE'])
def notice_detail(request, study_id, notice_id):

    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)

    notice = get_object_or_404(Notice, id=notice_id, study=study)
    
    # 공지사항 조회
    if request.method == 'GET':
        serializer = NoticeSerializer(notice)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 공지사항 수정
    elif request.method == 'PUT':
        # if notice.author != user:
        #     return Response(status=status.HTTP_403_FORBIDDEN)
        if membership.role not in ('leader', 'admin'):
            return error_list(NOT_AUTHORIZED)
        serializer = NoticeSerializer(notice, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    # 공지사항 삭제
    elif request.method == 'DELETE':
        if membership.role not in ('leader', 'admin'):
            return error_list(NOT_AUTHORIZED)
        notice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
@api_view(['GET'])
def notice_list(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    posts = Notice.objects.filter(study=study).order_by('-created_at')
    serializer = NoticeListSerializer(posts, many=True)
    return Response(serializer.data)

@login_required
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def uploaded_image(request, study_id):
    """
    이미지 업로드 할 때 호출되는 API
    """

    if "image" not in request.FILES:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    file_obj = request.FILES["image"]

    instance = UploadedImage.objects.create(image=file_obj)
    serializer = UploadedImageSerializer(instance)

    # 에디터가 필요한 응답 형태에 맞춰 URL 리턴
    return Response({
        "url": request.build_absolute_uri(serializer.data["image"])},
        status=status.HTTP_201_CREATED
    )