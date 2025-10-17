from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .forms import StudyCreateForm
from .models import Study, StudyMembership

# Create your views here.

# 스터디 생성
@csrf_exempt
@login_required
def create_study(request):
    """
    FormData로 보낸 데이터를 받아 스터디 생성
    """
    if request.method == 'POST':
        form = StudyCreateForm(request.POST or None, user=request.user)
        if form.is_valid():
            study = form.save()
            return JsonResponse({
                'id': study.id,
                'name': study.name,
                'leader': study.leader.username,
                'created_at': study.created_at,
            })
        else:
            return JsonResponse(form.errors, status=400)
    return JsonResponse({}, status=405)

# 스터디 가입
@require_POST
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
        return JsonResponse({'error': '가입된 스터디가 아닙니다.'}, status=400)
    
    if component.is_active:
        component.is_active = False
        component.save()
        return JsonResponse({'message': '탈퇴가 완료되었습니다.'}, status=200)
    else:
        return JsonResponse({'error': '이미 탈퇴한 스터디입니다.'}, status=400)

# 소속 스터디 조회
@login_required
def get_my_study(request):
    pass