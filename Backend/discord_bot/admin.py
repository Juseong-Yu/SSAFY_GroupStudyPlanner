from django.contrib import admin
from .models import DiscordStudyMapping, DiscordGuild

# Register your models here.
admin.site.register(DiscordStudyMapping)
admin.site.register(DiscordGuild)