from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Notice, Post
from studies.models import Study, StudyMembership
from .serializers import NoticeSerializer

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

# # 공지 수정
# @require_POST
# @login_required
# def update_notice(request):
#     study_id = request.POST.get("study_id")
#     notice_id = request.POST.get("notice_id")
#     user = request.user
#     study = get_object_or_404(Study, id=study_id)
#     notice = get_object_or_404(Notice, id=notice_id, study=study)
#     membership = StudyMembership.objects.filter(
#         user=user, study=study, is_active=True
#         ).first()
#     if not membership:
#         return JsonResponse(
#             {"error": "스터디 멤버가 아닙니다."},
#             status=403,
#             json_dumps_params={"ensure_ascii": False}
#         )
#     if membership.role not in ('leader', 'admin'):
#         return JsonResponse(
#             {"error": "공지사항 수정 권한이 없습니다."},
#             status=403,
#             json_dumps_params={"ensure_ascii": False}
#         )
#     # if notice.author != user:
#     #     return JsonResponse(
#     #         {"error": "본인만 수정 가능합니다."},
#     #         status=403
#     #     )
#     form = NoticeCreationForm(request.POST, instance=notice)
#     if form.is_valid():
#         form.save()
#         return JsonResponse(
#             {
#                 "message": "공지사항이 수정되었습니다.",
#                 "notice":{
#                     "id": notice.id,
#                     "title": notice.title,
#                     "content": notice.content,
#                     "study": study.name,
#                     "author": user.username,
#                     "created_at": notice.created_at.strftime("%Y-%m-%d %H:%M"),
#                     "updated_at": notice.updated_at.strftime("%Y-%m-%d %H:%M"),
#                 }
#             },
#             status=200,
#             json_dumps_params={"ensure_ascii": False}
#         )
#     else:
#         return JsonResponse(
#             {"error": form.errors},
#             status=400,
#             json_dumps_params={"ensure_ascii": False}
#         )

# # 공지 조회
# @login_required
# def read_notice(request):
#     study_id = request.GET.get("study_id")
#     notice_id = request.GET.get("notice_id")
#     user = request.user
#     study = get_object_or_404(Study, id=study_id)
#     notice = get_object_or_404(Notice, id=notice_id, study=study)
#     membership = StudyMembership.objects.filter(
#         user=user, study=study, is_active=True
#         ).first()
#     if not membership:
#         return JsonResponse({
#             "error": "스터디 멤버가 아닙니다.",
#         }, status=403, json_dumps_params={"ensure_ascii": False})

#     return JsonResponse({
#         "message": "조회 성공",
#         "notice": {
#             "id": notice.id,
#             "title": notice.title,
#             "content": notice.content,
#             "study": study.name,
#             "author": notice.author.username,
#             "created_at": notice.created_at.strftime("%Y-%m-%d %H:%M"),
#             "updated_at": notice.updated_at.strftime("%Y-%m-%d %H:%M"),
#         }
#     }, status=200, json_dumps_params={"ensure_ascii": False})

# # 공지 삭제
# @require_POST
# @login_required
# def delete_notice(request):
#     study_id = request.POST.get("study_id")
#     notice_id = request.POST.get("notice_id")
#     user = request.user
#     study = get_object_or_404(Study, id=study_id)
#     notice = get_object_or_404(Notice, id=notice_id, study=study)
#     membership = StudyMembership.objects.filter(
#         user=user, study=study, is_active=True
#         ).first()
#     if not membership:
#         return JsonResponse(
#             {"error": "스터디 멤버가 아닙니다."},
#             status=403,
#             json_dumps_params={"ensure_ascii": False}
#         )
#     if membership.role not in ('leader', 'admin'):
#         return JsonResponse(
#             {"error": "삭제 권한이 없습니다."},
#             status=403,
#             json_dumps_params={"ensure_ascii": False}
#         )
#     notice.delete()
#     return JsonResponse(
#         {"message": "삭제되었습니다.",},
#         status = 200, json_dumps_params={"ensure_ascii": False}
#     )