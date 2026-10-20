from app.repositories.interfaces.user_repository import UserRepository
from app.services.common import leads, permit, require


class UserService:
    def __init__(self, users: UserRepository, points):
        self.users, self.points = users, points

    def get(self, actor, identifier):
        user = require(self.users.get(identifier), "USER_NOT_FOUND")
        permit(actor.id == identifier or leads(actor, user.get("cellId")))
        return {
            k: v
            for k, v in {
                **user,
                "uid": identifier,
                "points": self.points.total(identifier),
                "level": user.get("level", 1),
            }.items()
            if k in ("id", "uid", "name", "email", "role", "points", "level", "cellId")
        }

    def patch(self, actor, identifier, data):
        permit(actor.id == identifier)
        self.get(actor, identifier)
        self.users.patch(identifier, data)
        return self.get(actor, identifier)
