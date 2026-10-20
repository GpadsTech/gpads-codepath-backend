from app.controllers.base import Controller
from app.schemas.base import validate
from app.schemas.user_schema import UserPatch


class UserController(Controller):
    def get(self, request, userId):
        return self.ok(self.services.users.get(request.user, userId))

    def patch(self, request, userId):
        return self.ok(
            self.services.users.patch(
                request.user, userId, validate(UserPatch, request.data)
            )
        )
