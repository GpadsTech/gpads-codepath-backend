from app.controllers.base import Controller


class PointsController(Controller):
    def get(self, request, userId):
        user = self.services.users.get(request.user, userId)
        return self.ok({"total": user["points"], "level": user["level"]})


class PointsHistoryController(Controller):
    def get(self, request, userId):
        self.services.users.get(request.user, userId)
        return self.ok(self.services.points.history(userId))
