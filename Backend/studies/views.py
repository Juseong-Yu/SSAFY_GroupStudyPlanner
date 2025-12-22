from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from .models import Study, StudyMembership, StudyJoinCode
from .serializers import StudySerializer, StudyMembersSerializer, StudyMembershipSerializer, StudyRoleSerializer, RoleSerializer

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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

            code = StudyJoinCode.objects.create(study = study)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 단일 스터디 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def get_my_role(request, study_id):
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)

    serializer = StudyRoleSerializer(membership)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_list(request, study_id):
    """
    스터디 멤버면 누구나 조회 가능
    """
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)

    serializer = StudyRoleSerializer(
        StudyMembership.objects.filter(study=study, is_active=True),
        many=True
    )
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def expel_member(request, study_id, user_id):
    """
    스터디 멤버 추방
    """
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    # 리더 제외 거부
    if membership.role != 'leader':
        return error_list(NOT_AUTHORIZED)

    target = get_object_or_404(User, id=user_id)

    if user == target:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    target_membership = get_object_or_404(StudyMembership, user=target, study=study, is_active=True)
    target_membership.is_active = False
    target_membership.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_role(request, study_id):
    """
    멤버 역할 변경
    """
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    # 리더 제외 거부
    if membership.role != 'leader':
        return error_list(NOT_AUTHORIZED)
    
    target_id = request.data.get('target_id')
    if not target_id:
        return Response({"detail": "target_id is required."},
                        status = status.HTTP_400_BAD_REQUEST)

    target = get_object_or_404(User, id=target_id)
    
    if user == target:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    target_membership = get_object_or_404(StudyMembership, user=target, study=study, is_active=True)

    serializer = RoleSerializer(target_membership, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def study_delete(request, study_id):
    """
    스터디 해산
    """
    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    # 리더 제외 거부
    if membership.role != 'leader':
        return error_list(NOT_AUTHORIZED)
    
    study.delete()
    return Response(status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def join_code(request, study_id):
    """
    스터디 참여 코드
    """

    user = request.user
    study = get_object_or_404(Study, id=study_id)
    membership = StudyMembership.objects.filter(
        user=user, study=study, is_active=True
    ).first()

    # 외부인 거부
    if not membership:
        return error_list(NOT_MEMBER)
    
    # 리더 제외 거부
    if membership.role != 'leader':
        return error_list(NOT_AUTHORIZED)

    if request.method == 'GET':
        code = get_object_or_404(StudyJoinCode, study=study)
        return Response({"join_code": code.join_code}, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        code = get_object_or_404(StudyJoinCode, study=study)
        code.update_join_code()
        return Response({"join_code": code.join_code}, status=status.HTTP_200_OK)