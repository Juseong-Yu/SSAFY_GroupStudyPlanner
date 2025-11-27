# exams/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("studies/<int:study_id>/exams/create/", views.create_exam),
    path("studies/<int:study_id>/exams/<int:exam_id>/", views.exam_detail),
]
