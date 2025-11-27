from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import DiscordGuild, DiscordStudyMapping
from .serializers import DiscordStudyMappingSerializer
from studies.models import Study

# Create your views here.

@login_required
@api_view(['POST'])
def connect_study(request, study_id):
    study = get_object_or_404(Study, id=study_id)
    data = request.data
    print(data)
    guild_id = data.get("guild_id")

    guild, _ = DiscordGuild.objects.update_or_create(
        id = guild_id,
        defaults = {
            "id": guild_id,
            "name": data.get("guild_name"),
            "icon_url": data.get("icon_url"),
            "is_active": True,
        }
    )

    mapping, _ = DiscordStudyMapping.objects.update_or_create(
        study = study,
        defaults = {"guild": guild},
    )
    serializer = DiscordStudyMappingSerializer(mapping)
    return Response(serializer.data, status=status.HTTP_200_OK)