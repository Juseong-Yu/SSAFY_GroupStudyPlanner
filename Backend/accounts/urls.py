from django.conf import settings
from django.conf.urls.static import static
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)