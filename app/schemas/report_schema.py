from rest_framework import serializers

from app.schemas.base import StrictSerializer


class ReportContent(StrictSerializer):
    reportDate = serializers.DateField(required=False)
    description = serializers.CharField(max_length=2000)
    report = serializers.CharField(
        max_length=200000, allow_blank=True, default="", trim_whitespace=False
    )
    code = serializers.CharField(
        max_length=200000, allow_blank=True, default="", trim_whitespace=False
    )

    def validate(self, data):
        if not data.get("report", "").strip() and not data.get("code", "").strip():
            raise serializers.ValidationError("Envie relatório ou código.")
        if "reportDate" in data:
            from django.utils import timezone
            if data["reportDate"] > timezone.localdate():
                raise serializers.ValidationError("A data de construção não pode ser futura.")
            data["reportDate"] = data["reportDate"].isoformat()
        return data


class ReportInput(ReportContent):
    challengeId = serializers.RegexField(r"^[A-Za-z0-9_-]{1,128}$")
