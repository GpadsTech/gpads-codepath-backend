from rest_framework import serializers

from app.schemas.base import StrictInteger, StrictSerializer


class EvaluationInput(StrictSerializer):
    decision = serializers.ChoiceField(choices=["approve", "reject"], default="approve")
    points = StrictInteger(min_value=0, max_value=100, required=False)
    feedback = serializers.CharField(max_length=10000, allow_blank=True, default="")
    repository = serializers.CharField(max_length=200, required=False)
    path = serializers.CharField(max_length=300, required=False)

    def validate(self, data):
        if data["decision"] == "approve" and not all(
            k in data for k in ("points", "repository", "path")
        ):
            raise serializers.ValidationError(
                "Aprovação requer pontos e destino GitHub."
            )
        if data["decision"] == "reject" and (
            not data["feedback"].strip()
            or any(k in data for k in ("points", "repository", "path"))
        ):
            raise serializers.ValidationError(
                "Devolução requer feedback e não aceita pontos/destino."
            )
        return data
