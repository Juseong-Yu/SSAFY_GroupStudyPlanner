from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('create_notice/', views.create_notice, name='create_notice'),
    path('update_notice/', views.update_notice, name='update_notice'),
    path('read_notice', views.read_notice, name='read_notice'),
    path('delete_notice', views.delete_notice, name='delete_notice'),

]