from django.urls import path
from . import views

app_name = 'discord'

urlpatterns = [
    path('connect_study/', views.connect_study, name='connect_study'),
    
]