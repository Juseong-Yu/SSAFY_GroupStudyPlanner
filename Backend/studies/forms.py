from django import forms
from .models import Study, StudyMembership
from django.contrib.auth import get_user_model

User = get_user_model()

class StudyCreateForm(forms.ModelForm):
    """
    스터디 생성 폼
    - 이름(name)을 입력받고
    - 생성한 사용자를 Study.leader 및 StudyMembership(리더)로 등록
    """
    class Meta:
        model = Study
        fields = ('name',)
    
    def __init__(self, *args, **kwargs):
        # view에서 전달된 user 객체를 받기 위해 추가
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        # 스터디 생성
        study = super().save(commit=False)

        if self.user:
            study.leader = self.user
        
        if commit:
            study.save()
            StudyMembership.objects.create(
                user=self.user,
                study=study,
                role='leader',
            )
        return study