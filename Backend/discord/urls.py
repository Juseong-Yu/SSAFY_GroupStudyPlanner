from django.urls import path
from . import views

app_name = 'discord'

urlpatterns = [
    path('connect_study/', views.connect_study, name='connect_study'),
    path('study_schedule_list/', views.study_schedule_list, name='study_schedule_list'),
    path('guild_schedule_list/', views.guild_schedule_list, name='guild_schedule_list'),
    
]