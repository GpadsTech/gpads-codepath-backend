from dataclasses import asdict
from uuid import uuid4

from app.models.challenge import Challenge
from app.repositories.interfaces.challenge_repository import ChallengeRepository
from app.services.common import now, permit, require


class ChallengeService:
    def __init__(self, challenges: ChallengeRepository):
        self.challenges = challenges

    def list(self, actor):
        return [
            c
            for c in self.challenges.list()
            if actor.role == "admin"
            or c["status"] == "active"
            and (
                not c.get("cellId")
                or c["cellId"] == actor.cellId
                or c["cellId"] in actor.ledCellIds
            )
        ]

    def get(self, actor, identifier):
        item = require(self.challenges.get(identifier), "CHALLENGE_NOT_FOUND")
        permit(
            actor.role == "admin"
            or not item.get("cellId")
            or item["cellId"] == actor.cellId
            or item["cellId"] in actor.ledCellIds
        )
        return item

    def create(self, actor, data):
        permit(actor.role == "admin")
        item = asdict(Challenge(id=uuid4().hex, createdAt=now(), **data))
        self.challenges.create(item["id"], item)
        return item

    def patch(self, actor, identifier, data):
        permit(actor.role == "admin")
        self.get(actor, identifier)
        self.challenges.patch(identifier, data)
        return self.get(actor, identifier)
