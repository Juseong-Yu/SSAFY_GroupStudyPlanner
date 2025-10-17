from django.urls import path
from . import views

app_name = 'studies'

urlpatterns = [
    path('create_study/', views.create_study, name='create_study'),
    
]