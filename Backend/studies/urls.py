from django.urls import path
from . import views

app_name = 'studies'

urlpatterns = [
    path('study/', views.study, name='study'),
    path('join/', views.join, name='join'),
    path('leave/', views.leave, name='leave'),
    path('study_list/', views.study_list, name='study_list'),
]