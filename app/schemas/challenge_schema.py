from rest_framework import serializers

from app.schemas.base import StrictInteger, StrictSerializer


class ChallengeInput(StrictSerializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=20000)
    status = serializers.ChoiceField(choices=["active", "inactive"], default="active")
    difficulty = serializers.ChoiceField(
        choices=["easy", "medium", "hard"], default="medium"
    )
    cellId = serializers.RegexField(
        r"^[A-Za-z0-9_-]{1,128}$", required=False, allow_null=True
    )
    points = StrictInteger(min_value=0, max_value=100, default=0)
