from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('study_schedule_create/', views.study_schedule_create, name='study_schedule_create'),
    path('<int:schedule_id>/study_schedule_detail/', views.study_schedule_detail, name='study_schedule_detail'),
    path('study_schedule_list/', views.study_schedule_list, name="study_schedule_list"),

]