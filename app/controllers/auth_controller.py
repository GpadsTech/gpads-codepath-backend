from app.controllers.base import Controller


class AuthController(Controller):
    def get(self, request):
        return self.ok(self.services.users.get(request.user, request.user.id))
