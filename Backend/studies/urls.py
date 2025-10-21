from django.urls import path
from . import views

app_name = 'studies'

urlpatterns = [
    path('create_study/', views.create_study, name='create_study'),
    path('join/', views.join, name='join'),
    path('leave/', views.leave, name='leave'),
    path('get_my_study/', views.get_my_study, name='get_my_study'),
    
]