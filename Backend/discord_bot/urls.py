from django.urls import path
from . import views
from .views import *

app_name = 'discord'

urlpatterns = [
    # path('connect_channel/', views.connect_channel, name='connect_channel'),
    path('study_schedule_list/', views.study_schedule_list, name='study_schedule_list'),
    path('channel_schedule_list/', views.channel_schedule_list, name='channel_schedule_list'),
    
    path("bot/invite/", DiscordBotInviteView.as_view()),
    path("bot/callback/", DiscordBotCallbackView.as_view()),
    path("<int:guild_id>/fetch_guild_channel/", FetchGuildChannel.as_view()),
    path("connect_channel/", DiscordStudyChannelConnectView.as_view()),
    path("get_connected_guild/", GetConnectedDiscordGuild.as_view()),
    
]