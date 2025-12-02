# exams/urls.py
from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    # ✅ 시험 생성
    path("",
        views.exam_collection,
        name="exam_collection",
    ),
    path(
        "ai-draft/<int:draft_id>/",
        views.exam_ai_draft_detail,
        name="exam-ai-draft-detail",
    ),
    # ⭐ AI 문제 생성 (여기 추가)
    path(
        "ai-generate/",
        views.exam_ai_generate,
        name="exam-ai-generate",
    ),
    path(
        "<int:exam_id>/",
        views.exam_detail,
        name="exam-detail",
    ),
    path(
        "<int:exam_id>/submit/",
        views.exam_submit,
        name="exam_submit",
    ),
    path(
        "<int:exam_id>/my_result/",
        views.exam_my_result,
        name="exam_my_result",
    ),
]
