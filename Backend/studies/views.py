from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import StudyCreateForm

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
                'success': True,
                'message': '스터디가 성공적으로 생성되었습니다.',
                'study': {
                    'id': study.id,
                    'name': study.name,
                    'leader': study.leader.username,
                    'created_at': study.created_at,
                }
            })
        else:
            return JsonResponse(form.errors, status=400)
    return JsonResponse({}, status=405)

# 스터디 가입
@login_required
def join_study(request):
    pass

# 소속 스터디 조회
@login_required
def get_my_study(request):
    pass