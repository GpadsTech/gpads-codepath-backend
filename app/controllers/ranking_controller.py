from app.controllers.base import Controller


class RankingController(Controller):
    def get(self, request):
        return self.ok(
            self.services.ranking.list(request.query_params.get("period", "all"))
        )


class RankingMeController(Controller):
    def get(self, request):
        return self.ok(
            self.services.ranking.me(
                request.user, request.query_params.get("period", "all")
            )
        )
