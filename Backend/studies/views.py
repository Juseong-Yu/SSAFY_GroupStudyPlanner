from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Study, StudyMembership
from .serializers import StudySerializer, StudyMembershipSerializer, StudyRoleSerializer

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

# 스터디 생성
@csrf_exempt
@login_required
@api_view(['POST'])
def study(request):
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
@login_required
@api_view(['GET'])
def study_detail(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()
    if not membership:
        return error_list(NOT_MEMBER)
    serializer = StudySerializer(study)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 스터디 가입
@login_required
@api_view(['POST'])
def join(request):
    study_id = request.data.get('id')
    study = get_object_or_404(Study, id=study_id)
    user = request.user

    # 기존 가입 여부 확인
    try:
        component = StudyMembership.objects.get(user=user, study=study)
        if component.is_active:
            return Response({'error': '이미 가입된 스터디입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            component.is_active = True
            component.save()
            return Response({'message': '재가입되었습니다.'}, status=status.HTTP_202_ACCEPTED) 
    except StudyMembership.DoesNotExist:
        StudyMembership.objects.create(
            user = request.user,
            study = study,
            role = 'member'
        )
        return Response({'message': '스터디에 가입되었습니다.'}, status=status.HTTP_201_CREATED)

# 스터디 탈퇴
@login_required
@api_view(['POST'])
def leave(request):
    study_id = request.data.get('id')
    study = get_object_or_404(Study, id=study_id)
    user = request.user

    try:
        component = StudyMembership.objects.get(user=user, study=study)
    except StudyMembership.DoesNotExist:
        return Response({'error': '가입된 스터디가 아닙니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if component.is_active:
        component.is_active = False
        component.save()
        return Response({'message': '탈퇴가 완료되었습니다.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': '이미 탈퇴한 스터디입니다.'}, status=status.HTTP_400_BAD_REQUEST)

# 소속 스터디 조회
@login_required
@api_view(['GET'])
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
    return Response({"studies": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_my_role(request, study_id):
    # user = request.user
    from accounts.models import User
    user = get_object_or_404(User, id=2)
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)

    serializer = StudyRoleSerializer(membership)
    return Response(serializer.data, status=status.HTTP_200_OK)