# exams/views.py
import json
import requests

from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from studies.models import Study
from .models import Exam, ExamQuestion, ExamAIDraft


# ====== GMS 설정 (settings.py 에서 가져오기) ======
GMS_API_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
GMS_KEY = 'S14P02AE06-7c0b7b86-468b-4efe-836e-3ff67dd5c373'


# ====== 파일에서 텍스트 뽑는 유틸 ======
def _extract_text_from_file(django_file) -> str:
    """
    업로드된 파일에서 텍스트 추출.
    - txt : utf-8 디코딩
    - docx: python-docx 설치되어 있으면 파싱
    """
    if not django_file:
        return ""

    content_type = django_file.content_type
    name = django_file.name.lower()

    try:
        # txt
        if content_type == "text/plain" or name.endswith(".txt"):
            return django_file.read().decode("utf-8", errors="ignore")

        # docx
        if name.endswith(".docx"):
            try:
                from docx import Document  # python-docx 필요
            except ImportError:
                return ""

            document = Document(django_file)
            paragraphs = [p.text for p in document.paragraphs]
            return "\n".join(paragraphs)

        return ""
    finally:
        django_file.close()


# ====== 1. 시험 리스트 / 생성 (GET, POST) ======
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def exam_collection(request, study_id: int):
    """
    GET  /studies/<study_id>/exams/   → 시험 리스트
    POST /studies/<study_id>/exams/   → 시험 생성
    """
    study = get_object_or_404(Study, pk=study_id)

    # ---- GET: 리스트 ----
    if request.method == "GET":
        exams = Exam.objects.filter(study=study).order_by("-created_at")

        data = []
        for exam in exams:
            data.append(
                {
                    "id": exam.id,
                    "title": exam.title,
                    "visibility": exam.visibility,
                    "due_at": exam.due_at,
                    "created_at": exam.created_at,
                    "question_count": exam.questions.count(),
                }
            )
        return Response(data, status=status.HTTP_200_OK)

    # ---- POST: 생성 ----
    body = request.data

    title = (body.get("title") or "").strip()
    if not title:
        return Response(
            {"error": "title은(는) 필수입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    visibility = body.get("visibility") or Exam.VISIBILITY_PUBLIC
    due_at = body.get("due_at") or None  # ISO 문자열이면 그대로 넣어도 Django가 대부분 파싱해줌

    questions = body.get("questions") or []
    if not isinstance(questions, list) or len(questions) == 0:
        return Response(
            {"error": "questions 배열이 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 기본 검증
    for idx, q in enumerate(questions, start=1):
        text = (q.get("text") or "").strip()
        if not text:
            return Response(
                {"error": f"문제 {idx}의 내용이 비어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        choices = q.get("choices") or []
        if len(choices) != 4:
            return Response(
                {"error": f"문제 {idx}의 보기 개수는 4개여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if q.get("correct_index") is None:
            return Response(
                {"error": f"문제 {idx}의 정답 인덱스를 선택해야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Exam 생성
    exam = Exam.objects.create(
        study=study,
        author=request.user,
        title=title,
        visibility=visibility,
        due_at=due_at,
    )

    # ExamQuestion 생성
    for order, q in enumerate(questions, start=1):
        ExamQuestion.objects.create(
            exam=exam,
            order=order,
            text=(q.get("text") or "").strip(),
            choices=q.get("choices"),
            correct_index=int(q.get("correct_index")),
        )

    # 필요하면 ai_draft_id 도 같이 저장해서 추적 가능
    # ai_draft_id = body.get("ai_draft_id")

    return Response({"id": exam.id}, status=status.HTTP_201_CREATED)


# ====== 2. 시험 상세 (GET) ======
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_detail(request, study_id: int, exam_id: int):
    """
    GET /studies/<study_id>/exams/<exam_id>/
    """
    exam = get_object_or_404(Exam, pk=exam_id, study_id=study_id)

    data = {
        "id": exam.id,
        "title": exam.title,
        "visibility": exam.visibility,
        "due_at": exam.due_at,
        "created_at": exam.created_at,
        "author": {
            "id": exam.author.id,
            "username": exam.author.username,
            "email": exam.author.email,
        },
        "questions": [
            {
                "id": q.id,
                "order": q.order,
                "text": q.text,
                "choices": q.choices,
                "correct_index": q.correct_index,
            }
            for q in exam.questions.all().order_by("order")
        ],
    }
    return Response(data, status=status.HTTP_200_OK)


# ====== 3. AI로 시험 초안 생성 (POST, FormData) ======
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def exam_ai_generate(request, study_id: int):
    """
    POST /studies/<study_id>/exams/ai-generate/

    FormData:
      - title
      - question_count
      - visibility (선택)
      - due_at (선택, ISO 문자열)
      - context_text (선택)
      - context_file (선택, txt / docx 등)
    """
    study = get_object_or_404(Study, pk=study_id)

    title = (request.data.get("title") or "").strip()
    visibility = request.data.get("visibility")
    due_at = request.data.get("due_at")

    raw_qc = request.data.get("question_count") or "5"
    try:
        question_count = int(raw_qc)
    except ValueError:
        return Response(
            {"error": "question_count는 정수여야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if question_count <= 0:
        return Response(
            {"error": "question_count는 1 이상이어야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    context_text = (request.data.get("context_text") or "").strip()
    context_file = request.FILES.get("context_file")

    file_text = _extract_text_from_file(context_file) if context_file else ""
    pieces = [context_text, file_text]
    data_info = "\n\n".join([p for p in pieces if p])

    if not data_info:
        return Response(
            {"error": "context_text 또는 context_file 중 하나는 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---- LLM 프롬프트 구성 ----
    prompt = f"""
다음 데이터 설명과 내용을 바탕으로 객관식 {question_count}문항의 4지선다 문제를 만들어줘.

데이터 설명과 내용:
{data_info}

문항은 한국어로 만들고, 출력은 JSON 형식만 사용해.

출력 형식(JSON만):
[
  {{
    "question": "문제 내용",
    "options": ["보기1", "보기2", "보기3", "보기4"],
    "answer_index": 0
  }}
]
"""

    payload = {
        "model": "gpt-5-nano",
        "messages": [
            {"role": "developer", "content": "JSON 형식만 출력해 주세요."},
            {"role": "user", "content": prompt},
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}",
    }

    # ---- GMS API 호출 ----
    try:
        gms_res = requests.post(GMS_API_URL, headers=headers, json=payload, timeout=60)
    except requests.RequestException as e:
        return Response(
            {"error": "GMS API 요청 중 오류가 발생했습니다.", "detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if gms_res.status_code != 200:
        return Response(
            {
                "error": f"GMS API Error {gms_res.status_code}",
                "detail": gms_res.text,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = gms_res.json()
    content = data["choices"][0]["message"]["content"]

    # ---- JSON 파싱 ----
    try:
        quiz_list = json.loads(content)
    except Exception:
        return Response(
            {"error": "LLM 응답 JSON 파싱 실패", "raw_content": content},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    questions_for_payload = []
    for item in quiz_list:
        q_text = item.get("question", "")
        options = item.get("options", [])
        answer_idx = item.get("answer_index", 0)

        if not isinstance(options, list):
            options = []
        options = (options + ["", "", "", ""])[:4]

        try:
            correct_idx = int(answer_idx)
        except (ValueError, TypeError):
            correct_idx = 0
        if correct_idx < 0 or correct_idx > 3:
            correct_idx = 0

        questions_for_payload.append(
            {
                "text": q_text,
                "choices": options,
                "correctIndex": correct_idx,
            }
        )

    # 기본 제목
    if not title:
        title = f"{study.name} 시험"

    draft_payload = {
        "title": title,
        "questions": questions_for_payload,
        "meta": {
            "visibility": visibility,
            "due_at": due_at,
            "question_count": question_count,
        },
    }

    draft = ExamAIDraft.objects.create(
        study=study,
        author=request.user,
        payload=draft_payload,
    )

    return Response(
        {
            "draft_id": draft.id,
            "question_count": len(questions_for_payload),
        },
        status=status.HTTP_201_CREATED,
    )


# ====== 4. AI Draft 상세 (GET) ======
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_ai_draft_detail(request, study_id: int, draft_id: int):
    """
    GET /studies/<study_id>/exams/ai-draft/<draft_id>/
    → ExamEditorPage.vue 에서 초기 값 세팅할 때 사용
    """
    draft = get_object_or_404(
        ExamAIDraft,
        pk=draft_id,
        study_id=study_id,
        author=request.user,  # 본인이 만든 Draft만 조회
    )
    return Response(draft.payload, status=status.HTTP_200_OK)
