from rest_framework import serializers


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) - set(self.fields):
            raise serializers.ValidationError(
                {"non_field_errors": ["Campos desconhecidos ou objeto inválido."]}
            )
        return super().to_internal_value(data)


class StrictInteger(serializers.IntegerField):
    def to_internal_value(self, data):
        if type(data) is not int:
            raise serializers.ValidationError("Use um inteiro JSON.")
        return super().to_internal_value(data)


def validate(schema, data, partial=False):
    serializer = schema(data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data
