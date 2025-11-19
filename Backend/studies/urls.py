from django.urls import path, include
from . import views

app_name = 'studies'

urlpatterns = [
    path('study/', views.study, name='study'),
    path('join/', views.join, name='join'),
    path('leave/', views.leave, name='leave'),
    path('<int:study_id>', views.study_detail, name='study_detail'),
    path('study_list/', views.study_list, name='study_list'),
    path('<int:study_id>/posts/', include('posts.urls')),
    
]