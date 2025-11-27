from rest_framework import serializers
from .models import Exam, Question, ChoiceOption
from studies.models import Study


class QuestionSerializer(serializers.ModelSerializer):
    # options: ["보기1", "보기2", "보기3", "보기4"]
    options = serializers.ListField(
        child=serializers.CharField(),
        min_length=4,
        max_length=4,
    )

    class Meta:
        model = Question
        fields = ("text", "order", "answer_index", "options")


class ExamCreateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = ("title", "description", "deadline", "questions")

    def create(self, validated_data):
        """
        study는 URL에서, user는 request에서 context로 받아온다.
        """
        request = self.context.get("request")
        study = self.context.get("study")

        user = getattr(request, "user", None)
        questions_data = validated_data.pop("questions")

        exam = Exam.objects.create(
            study=study,
            created_by=user,
            **validated_data,
        )

        for idx, q_data in enumerate(questions_data):
            options_texts = q_data.pop("options")
            order = q_data.get("order", idx + 1)

            question = Question.objects.create(
                exam=exam,
                order=order,
                **q_data,
            )

            for o_idx, text in enumerate(options_texts):
                ChoiceOption.create(
                    question=question,
                    text=text,
                    order=o_idx,
                )

        return exam

class ChoiceOptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceOption
        fields = ("order", "text")


class QuestionDetailSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "order", "text", "answer_index", "options")

    def get_options(self, obj):
        return [
            option.text
            for option in obj.options.order_by("order")
        ]


class ExamDetailSerializer(serializers.ModelSerializer):
    questions = QuestionDetailSerializer(many=True)

    class Meta:
        model = Exam
        fields = (
            "id",
            "study",
            "title",
            "description",
            "deadline",
            "questions",
        )
