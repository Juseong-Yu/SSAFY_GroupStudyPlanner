from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('notice_create/', views.notice_create, name='notice_create'),
    path('notice_detail/<int:notice_id>/', views.notice_detail, name='notice_detail'),
    path('notice_list/', views.notice_list, name='notice_list'),
    path('upload_img/', views.uploaded_image, name='upload_image'),
    
]