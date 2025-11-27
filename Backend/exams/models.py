from django.db import models
from django.conf import settings
from studies.models import Study

class Exam(models.Model):
    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="exams",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_exams",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=1)
    answer_index = models.PositiveSmallIntegerField()  # 0~3

    def __str__(self) -> str:
        return f"[{self.exam_id}] Q{self.order}: {self.text[:20]}"


class ChoiceOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()  # 0,1,2,3

    def __str__(self) -> str:
        return f"Q{self.question_id} - #{self.order}: {self.text[:15]}"
