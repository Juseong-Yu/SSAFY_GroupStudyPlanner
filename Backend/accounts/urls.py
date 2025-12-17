from django.urls import path
from . import views
from .views import ProtectedView, LogoutView, DiscordCallbackView, RegisterView

app_name = 'accounts'

urlpatterns = [
    path("csrf/", views.csrf, name="csrf"),
    # path('login/', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),
    path('update/', views.update, name='update'),
    # path('delete/', views.delete, name='delete'),
    path('password/', views.password_change, name='password_change'),
    path('search/', views.search, name='search'),
    path('check_password/', views.verify_password, name='check_password'),
    path('signup/', RegisterView.as_view(), name="signup"),
    path('logout/', LogoutView.as_view()),
    path('some-protected-endpoint/', ProtectedView.as_view()),
    # path("auth/discord/callback/", DiscordCallbackView.as_view(), name="discord_callback"),

    path("connect_discord/", views.connect_discord, name="connect_discord"),
    path("auth/discord/callback/", views.discord_callback, name="discord_callback"),
    path("login_with_discord/", views.login_with_discord, name="login_with_discord"),
    path("auth/discord/login/callback/", views.discord_login_callback, name="discord_login_callback"),
    
]