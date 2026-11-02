from rest_framework import serializers
from app.controllers.base import Controller
from app.schemas.base import StrictSerializer, validate

class AIInput(StrictSerializer):
    activities = serializers.CharField(max_length=12000)
    code = serializers.CharField(max_length=30000, allow_blank=True, default='')

class AIController(Controller):
    def get(self, request):
        return self.ok(self.services.ai.usage(request.user))

    def post(self, request):
        return self.ok(self.services.ai.generate(request.user, validate(AIInput, request.data)))
