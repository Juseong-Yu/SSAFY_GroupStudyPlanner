from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path("csrf/", views.csrf, name="csrf"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('update/', views.update, name='update'),
    path('delete/', views.delete, name='delete'),
    path('signup/', views.signup, name='signup'),
    path('password/', views.password, name='password'),
    path('search/', views.search, name='search'),
    path('check_password/', views.check_password, name='check_password'),
]