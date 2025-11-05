from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import NoticeCreationForm
from .models import Notice, Post
from studies.models import Study, StudyMembership

# Create your views here.
@ login_required
def create_notice(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user,
        study=study,
        is_active=True,
    )
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
    
    if request.method == 'POST':
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
    return JsonResponse(
        {"error": "POST 요청만 허용됩니다."},
        status=405,
        json_dumps_params={"ensure_ascii": False}
    )