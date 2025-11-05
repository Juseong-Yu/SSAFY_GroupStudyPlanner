from django import forms
from .models import Post, Notice

class NoticeCreationForm(forms.ModelForm):
    """
    공지 작성 폼
    스터디, 작성자 속성은 view에서 채워 넣음
    """
    class Meta:
        model = Notice
        fields = ('title', 'content')