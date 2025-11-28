# exams/serializers.py
from rest_framework import serializers
from .models import Exam, ExamQuestion, ExamAIDraft


class ExamQuestionCreateSerializer(serializers.Serializer):
    text = serializers.CharField()
    choices = serializers.ListField(
        child=serializers.CharField(),
        min_length=4,
        max_length=4,
    )
    correct_index = serializers.IntegerField(min_value=0, max_value=3)


class ExamCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    visibility = serializers.ChoiceField(choices=[c[0] for c in Exam.VISIBILITY_CHOICES])
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    questions = ExamQuestionCreateSerializer(many=True)
    ai_draft_id = serializers.IntegerField(required=False, allow_null=True)


class ExamQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamQuestion
        fields = ['id', 'order', 'text', 'choices', 'correct_index']


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = ExamQuestionSerializer(many=True, read_only=True)
    study_id = serializers.IntegerField(source='study.id')

    class Meta:
        model = Exam
        fields = [
            'id',
            'study_id',
            'title',
            'visibility',
            'due_at',
            'questions',
            'created_at',
            'updated_at',
        ]


class ExamAIDraftSerializer(serializers.Serializer):
    """
    프론트에서 기대하는 형태대로 변환
    { "title": "...", "questions": [{ text, choices, correctIndex }] }
    """
    title = serializers.CharField()
    questions = serializers.ListField()
