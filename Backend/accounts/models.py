from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    profile_img = models.ImageField(upload_to='profile_img/', blank=True, null=True)
    discord_id = models.CharField(max_length=100, null=True, blank=True)
    discord_refresh_token = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']