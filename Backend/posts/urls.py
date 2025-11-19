from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('create_notice/', views.notice_create, name='notice_create'),
    path('notice_detail/<int:notice_id>', views.notice_detail, name='notice_detail'),

]