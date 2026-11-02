from rest_framework import serializers
from app.controllers.base import Controller
from app.schemas.base import StrictSerializer, validate

class RegistrationInput(StrictSerializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(min_length=8, max_length=128, trim_whitespace=False, write_only=True)
    role = serializers.ChoiceField(choices=['student'])
    cellId = serializers.RegexField(r'^[A-Za-z0-9_-]{1,128}$', required=False)

class RegistrationController(Controller):
    def get(self, request):
        return self.ok(self.services.registration.list(request.user))

    def post(self, request):
        return self.ok(self.services.registration.create(request.user, validate(RegistrationInput, request.data)), 201)
