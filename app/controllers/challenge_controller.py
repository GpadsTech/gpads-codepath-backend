from app.controllers.base import Controller
from app.schemas.base import validate
from app.schemas.challenge_schema import ChallengeInput


class ChallengeListController(Controller):
    def get(self, request):
        return self.ok(self.services.challenges.list(request.user))

    def post(self, request):
        return self.ok(
            self.services.challenges.create(
                request.user, validate(ChallengeInput, request.data)
            ),
            201,
        )


class ChallengeController(Controller):
    def get(self, request, challengeId):
        return self.ok(self.services.challenges.get(request.user, challengeId))

    def patch(self, request, challengeId):
        return self.ok(
            self.services.challenges.patch(
                request.user,
                challengeId,
                validate(ChallengeInput, request.data, partial=True),
            )
        )

    def delete(self, request, challengeId):
        return self.ok(
            self.services.challenges.patch(
                request.user, challengeId, {"status": "inactive"}
            )
        )
