from app.controllers.base import Controller


class DashboardController(Controller):
    def get(self, request):
        return self.ok(self.services.dashboard.get(request.user))
