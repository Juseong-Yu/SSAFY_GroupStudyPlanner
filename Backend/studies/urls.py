from django.urls import path, include
from . import views

app_name = 'studies'

urlpatterns = [
    path('study/', views.study, name='study'),
    path('join/', views.join, name='join'),
    path('leave/', views.leave, name='leave'),
    path('<int:study_id>/', views.study_detail, name='study_detail'),
    path('study_list/', views.study_list, name='study_list'),
    path('<int:study_id>/get_my_role/', views.get_my_role, name='get_my_role'),
    path('<int:study_id>/member_list/', views.member_list, name='member_list'),
    path('<int:study_id>/<int:user_id>/expel_member/', views.expel_member, name='experl_member'),
    path('<int:study_id>/change_role/', views.change_role, name='change_role'),
    path('<int:study_id>/study_delete/', views.study_delete, name='study_delete'),

    path('<int:study_id>/posts/', include('posts.urls')),
    path('<int:study_id>/schedules/', include('schedules.urls')),
    path('<int:study_id>/discord/', include('discord_bot.urls')),
    path('<int:study_id>/exams/', include('exams.urls')),
]