# exams/models.py
from django.db import models
from django.conf import settings

# 너 프로젝트의 Study 모델 경로에 맞게 수정해줘
from studies.models import Study  # 예시


class Exam(models.Model):
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_SCORE_ONLY = 'score_only'
    VISIBILITY_PRIVATE = 'private'

    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, '모두 공개'),
        (VISIBILITY_SCORE_ONLY, '내 점수만 공개'),
        (VISIBILITY_PRIVATE, '리더만 확인'),
    ]

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='exams',
    )
    title = models.CharField(max_length=255)
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PUBLIC,
    )
    due_at = models.DateTimeField(null=True, blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_exams',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.study_id})'


class ExamQuestion(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    order = models.PositiveIntegerField()
    text = models.TextField()

    # ["보기1", "보기2", "보기3", "보기4"]
    choices = models.JSONField(default=list)

    # 0~3 중 하나 (4지선다)
    correct_index = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Q{self.order}: {self.text[:30]}'


class ExamAIDraft(models.Model):

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name='exam_ai_drafts',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_ai_drafts',
    )
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'AI Draft #{self.id} for study {self.study_id}'


class ExamResult(models.Model):
    exam = models.ForeignKey(
        'Exam',
        on_delete=models.CASCADE,
        related_name='results'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_results'
    )

    score = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)

    submitted_at = models.DateTimeField(auto_now_add=True)

    # 선택사항 (유저 답안 저장하고 싶을 때)
    answers = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('exam', 'user')  # 한 사람당 한 번만 제출

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.score}점)"
