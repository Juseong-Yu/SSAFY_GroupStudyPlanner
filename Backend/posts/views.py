from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import NoticeCreationForm
from .models import Notice, Post
from studies.models import Study, StudyMembership

# Create your views here.
@require_POST
@login_required
def create_notice(request):
    user = request.user
    study_id = request.POST.get("study_id")
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
        ).first()
    if not membership:
        return JsonResponse(
            {"error": "스터디 멤버가 아닙니다."},
            status=403,
            json_dumps_params={"ensure_ascii": False}
        )
    if membership.role not in ('leader', 'admin'):
        return JsonResponse(
            {"error": "공지사항 작성 권한이 없습니다."},
            status=403,
            json_dumps_params={"ensure_ascii": False}
        )

    form = NoticeCreationForm(request.POST)
    if form.is_valid():
        notice = form.save(commit=False)
        notice.study = study
        notice.author = user
        notice.save()
        return JsonResponse(
            {
                "message": "공지사항이 작성되었습니다.",
                "notice":{
                    "id": notice.id,
                    "title": notice.title,
                    "content": notice.content,
                    "study": study.name,
                    "author": user.username,
                    "created_at": notice.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            },
            status=201,
            json_dumps_params={"ensure_ascii": False}
        )
    else:
        return JsonResponse(
            {"error": form.errors},
            status=400,
            json_dumps_params={"ensure_ascii": False}
        )

@require_POST
@login_required
def update_notice(request):
    study_id = request.POST.get("study_id")
    notice_id = request.POST.get("notice_id")
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    notice = get_object_or_404(Notice, id=notice_id, study=study)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
        ).first()
    if not membership:
        return JsonResponse(
            {"error": "스터디 멤버가 아닙니다."},
            status=403,
            json_dumps_params={"ensure_ascii": False}
        )
    if membership.role not in ('leader', 'admin'):
        return JsonResponse(
            {"error": "공지사항 수정 권한이 없습니다."},
            status=403,
            json_dumps_params={"ensure_ascii": False}
        )
    # if notice.author != user:
    #     return JsonResponse(
    #         {"error": "본인만 수정 가능합니다."},
    #         status=403
    #     )
    form = NoticeCreationForm(request.POST, instance=notice)
    if form.is_valid():
        form.save()
        return JsonResponse(
            {
                "message": "공지사항이 수정되었습니다.",
                "notice":{
                    "id": notice.id,
                    "title": notice.title,
                    "content": notice.content,
                    "study": study.name,
                    "author": user.username,
                    "created_at": notice.created_at.strftime("%Y-%m-%d %H:%M"),
                    "updated_at": notice.updated_at.strftime("%Y-%m-%d %H:%M"),
                }
            },
            status=200,
            json_dumps_params={"ensure_ascii": False}
        )
    else:
        return JsonResponse(
            {"error": form.errors},
            status=400,
            json_dumps_params={"ensure_ascii": False}
        )

@login_required
def read_notice(request):
    study_id = request.GET.get("study_id")
    notice_id = request.GET.get("notice_id")
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    notice = get_object_or_404(Notice, id=notice_id, study=study)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
        ).first()
    if not membership:
        return JsonResponse({
            "error": "스터디 멤버가 아닙니다.",
        }, status=403, json_dumps_params={"ensure_ascii": False})

    return JsonResponse({
        "message": "조회 완료",
        "notice": {
            "id": notice.id,
            "title": notice.title,
            "content": notice.content,
            "study": study.name,
            "author": notice.author.username,
            "created_at": notice.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": notice.updated_at.strftime("%Y-%m-%d %H:%M"),
        }
    }, status=200, json_dumps_params={"ensure_ascii": False})