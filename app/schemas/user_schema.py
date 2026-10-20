from rest_framework import serializers

from app.schemas.base import StrictSerializer


class UserPatch(StrictSerializer):
    name = serializers.CharField(max_length=120)
