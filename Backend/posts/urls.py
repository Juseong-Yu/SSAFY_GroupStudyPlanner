from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('create_notice/', views.create_notice, name='create_notice'),
    
]