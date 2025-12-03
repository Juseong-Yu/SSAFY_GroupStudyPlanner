from django.urls import path
from . import views

app_name = 'discord'

urlpatterns = [
    path('connect_channel/', views.connect_channel, name='connect_channel'),
    path('study_schedule_list/', views.study_schedule_list, name='study_schedule_list'),
    path('channel_schedule_list/', views.channel_schedule_list, name='channel_schedule_list'),
    
]