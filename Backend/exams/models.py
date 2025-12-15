# exams/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone  # ✅ 추가 (아래 메서드들에서 사용)

from studies.models import Study


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

    # ✅ 새로 추가: 시험 시작 시간 (없으면 바로 응시 가능)
    start_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='시험 입장 가능 시작 시각 (비워두면 바로 응시 가능)'
    )

    # ✅ 기존 필드: 시험 끝나는 시간(마감 시간)
    # 네가 말한 "끝나는 시간" == 여기 due_at 으로 사용
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='시험 응시 마감 시각 (비워두면 시간 제한 없음)'
    )

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

    # --------------------------
    # ⬇ 편하게 쓰라고 상태/타이머용 헬퍼 메서드들
    # --------------------------

    def can_enter_now(self, now=None) -> bool:
        """
        지금 시점에 시험 입장이 가능한지 여부.
        - start_at이 있고 아직 그 전이면 False
        - due_at이 있고 이미 지났으면 False
        """
        if now is None:
            now = timezone.now()

        # 시작 전이면 입장 불가
        if self.start_at and now < self.start_at:
            return False

        # 마감 이후면 입장 불가
        if self.due_at and now > self.due_at:
            return False

        return True

    def get_status(self, now=None) -> str:
        """
        시험 상태 문자열 리턴:
        - 'scheduled' : 시작 전 (start_at > now)
        - 'ongoing'   : 진행 중 (입장 가능)
        - 'ended'     : 마감 이후
        """
        if now is None:
            now = timezone.now()

        if self.due_at and now > self.due_at:
            return 'ended'

        if self.start_at and now < self.start_at:
            return 'scheduled'

        return 'ongoing'

    def get_remaining_seconds(self, now=None):
        """
        마감 시각(due_at)이 있을 때 남은 시간(초)을 리턴.
        - due_at이 없으면 None
        - 이미 지났으면 0
        """
        if self.due_at is None:
            return None

        if now is None:
            now = timezone.now()

        diff = (self.due_at - now).total_seconds()
        return max(0, int(diff))



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
