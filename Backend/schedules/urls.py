from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('study_schedule_create/', views.study_schedule_create, name='study_schedule_create'),
    path('study_schedule_list/', views.study_schedule_list, name="study_schedule_list"),
    path('<int:schedule_id>/study_schedule_detail/', views.study_schedule_detail, name='study_schedule_detail'),
    path('personal_schedule_create/', views.personal_schedule_create, name='personal_schedule_create'),
    path('personal_schedule_list/', views.personal_schedule_list, name='personal_schedule_list'),
    path('<int:schedule_id/personal_schedule_detail/', views.personal_schedule_detail, name='personal_schedule_detail'),
]