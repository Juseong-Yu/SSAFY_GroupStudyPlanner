from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Study, StudyMembership
from .serializers import StudySerializer, StudyMembershipSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Study, StudyMembership

# Create your views here.

# 스터디 생성
@csrf_exempt
@api_view(['POST', 'GET'])
@login_required
def study(request):
    # 스터디 생성
    if request.method == 'POST':
        serializer = StudySerializer(data=request.data)
        if serializer.is_valid():
            # 스터디 객체를 저장
            study = serializer.save(leader = request.user)

            # StudyMembership 객체 생성
            StudyMembership.objects.create(
                user=request.user, 
                study=study,       
                role='leader',     
                is_active=True     
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 단일 스터디 조회
    elif request.method == 'GET':
        study_id = request.GET.get('id')
        try:
            study = Study.objects.get(pk=study_id)
        except:
            return Response({"detail": "스터디가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudySerializer(study)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 스터디 가입
@api_view(['POST'])
@login_required
def join(request):
    study_id = request.POST.get('id')
    study = get_object_or_404(Study, id=study_id)
    user = request.user

    # 기존 가입 여부 확인
    try:
        component = StudyMembership.objects.get(user=user, study=study)
        if component.is_active:
            return JsonResponse({'error': '이미 가입된 스터디입니다.'}, status=400)
        else:
            component.is_active = True
            component.save()
            return JsonResponse({'message': '재가입되었습니다.'}, status=201) 
    except StudyMembership.DoesNotExist:
        StudyMembership.objects.create(
            user = request.user,
            study = study,
            role = 'member'
        )
        return JsonResponse({'message': '스터디에 가입되었습니다.'}, status=201)

# 스터디 탈퇴
@require_POST
@login_required
def leave(request):
    study_id = request.POST.get('id')
    study = get_object_or_404(Study, id=study_id)
    user = request.user

    try:
        component = StudyMembership.objects.get(user=user, study=study)
    except StudyMembership.DoesNotExist:
        return JsonResponse({'error': '가입된 스터디가 아닙니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if component.is_active:
        component.is_active = False
        component.save()
        return JsonResponse({'message': '탈퇴가 완료되었습니다.'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error': '이미 탈퇴한 스터디입니다.'}, status=status.HTTP_400_BAD_REQUEST)

# 소속 스터디 조회
@api_view(['GET'])
@login_required
def study_list(request):
    """
    로그인한 사용자가 속한 스터디 목록을 JSON으로 반환하는 함수
    중간 테이블(StudyMembership)을 이용해 사용자-스터디 관계를 조회
    """
    user = request.user

    # 사용자가 속한 모든 스터디 멤버십 조회 (is_active=True로 필터)
    memberships = StudyMembership.objects.filter(user=user, is_active=True).select_related('study')
    # 직렬화하여 응답
    serializer = StudyMembershipSerializer(memberships, many=True)
    print(serializer.data)
    return Response({"studies": serializer.data}, status=status.HTTP_200_OK)

# 특정 스터디 조회
@api_view(['GET'])
@login_required
def this_study(request):
    study_id = request.GET.get('id')
    study = get_object_or_404(Study, pk=study_id)
    serializer = StudySerializer(study)
    return Response(serializer.data, status=status.HTTP_200_OK)