# views.py
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

GMS_API_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
GMS_KEY = 'S14P02AE06-7c0b7b86-468b-4efe-836e-3ff67dd5c373'   # settings.py에 넣어야 함

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import ExamCreateSerializer
from studies.models import Study
from .models import Exam
from .serializers import ExamDetailSerializer

@api_view(["POST"])
@permission_classes([IsAuthenticated])  # 개발 중엔 AllowAny로 잠깐 풀어도 됨
def create_exam(request, study_id: int):
    """
    URL의 study_id를 기준으로 해당 스터디에 속한 Exam + Questions 생성
    """

    # 1) study_id로 스터디 찾기
    try:
        study = Study.objects.get(pk=study_id)
    except Study.DoesNotExist:
        return Response(
            {"detail": "해당 스터디를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 2) serializer로 body 검증 + study, request context로 전달
    serializer = ExamCreateSerializer(
        data=request.data,
        context={
            "request": request,
            "study": study,
        },
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    exam = serializer.save()

    # 3) 응답은 일단 exam 요약 정보만 내려주자
    return Response(
        {
            "id": exam.id,
            "study_id": study.id,
            "title": exam.title,
            "description": exam.description,
            "deadline": exam.deadline,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # 개발 중엔 AllowAny 가능
def exam_detail(request, study_id: int, exam_id: int):
    # 스터디 존재 확인
    try:
        study = Study.objects.get(pk=study_id)
    except Study.DoesNotExist:
        return Response({"detail": "존재하지 않는 스터디입니다."}, status=404)
    
    # 시험 존재 + 스터디 일치 확인
    try:
        exam = Exam.objects.get(pk=exam_id, study=study)
    except Exam.DoesNotExist:
        return Response({"detail": "해당 스터디에 시험이 없습니다."}, status=404)

    serializer = ExamDetailSerializer(exam)
    return Response(serializer.data, status=200)


@csrf_exempt
def maketest(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    body = json.loads(request.body.decode("utf-8"))

    data_info = body.get("data_info")
    num_questions = body.get("num_questions")

    # LLM 프롬프트 완성
    prompt = f"""
데이터 설명 기반으로 객관식 {num_questions}문항 생성해줘.

데이터:
{data_info}

출력 형식(JSON만):
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer_index": 0
  }}
]
"""

    payload = {
        "model": "gpt-5-nano",
        "messages": [
            {"role": "developer", "content": "JSON 형식만 출력"},
            {"role": "user", "content": prompt},
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}",
    }

    # ⭐ GMS Proxy 로 요청 보내기
    response = requests.post(
        GMS_API_URL,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return JsonResponse({
            "error": f"GMS API Error {response.status_code}",
            "detail": response.text
        }, status=500)

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    try:
        quiz = json.loads(content)
    except:
        return JsonResponse({
            "error": "JSON 파싱 실패",
            "raw_content": content
        }, status=200)

    return JsonResponse({"quiz": quiz}, status=200)

