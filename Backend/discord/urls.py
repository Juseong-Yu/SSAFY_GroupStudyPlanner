from django.urls import path
from . import views

app_name = 'discord'

urlpatterns = [
    path('connect_channel/', views.connect_channel, name='connect_channel'),
    path('study_schedule_list/', views.study_schedule_list, name='study_schedule_list'),
    path('guild_schedule_list/', views.guild_schedule_list, name='guild_schedule_list'),
    
]