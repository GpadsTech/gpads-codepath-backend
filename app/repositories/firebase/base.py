from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore

from app.exceptions.application_exceptions import ApplicationError
from app.repositories.interfaces.repositories import Repositories


def persistence_error():
    return ApplicationError(
        "PERSISTENCE_ERROR", "Falha ao acessar a persistência. Tente novamente.", 500
    )


class FirebaseDocumentRepository:
    def __init__(self, db, collection: str, transaction=None):
        self.collection = db.collection(collection)
        self.transaction = transaction

    def get(self, identifier: str) -> dict | None:
        try:
            result = self.collection.document(identifier).get(
                transaction=self.transaction
            )
            return {**result.to_dict(), "id": result.id} if result.exists else None
        except GoogleAPICallError as exc:
            raise persistence_error() from exc

    def list(self) -> list[dict]:
        try:
            return [
                {**item.to_dict(), "id": item.id}
                for item in self.collection.stream(transaction=self.transaction)
            ]
        except GoogleAPICallError as exc:
            raise persistence_error() from exc

    def create(self, identifier: str, data: dict) -> None:
        try:
            reference = self.collection.document(identifier)
            if self.transaction is not None:
                self.transaction.create(reference, data)
            else:
                reference.create(data)
        except GoogleAPICallError as exc:
            raise persistence_error() from exc

    def patch(self, identifier: str, data: dict) -> None:
        try:
            reference = self.collection.document(identifier)
            if self.transaction is not None:
                self.transaction.update(reference, data)
            else:
                reference.update(data)
        except GoogleAPICallError as exc:
            raise persistence_error() from exc


class FirebaseUnitOfWork:
    """Retries pure business callbacks; all reads must precede writes."""

    def __init__(self, db):
        self.db = db

    def run(self, operation):
        @firestore.transactional
        def execute(transaction):
            return operation(make_repositories(self.db, transaction))

        try:
            return execute(self.db.transaction())
        except (GoogleAPICallError, ValueError) as exc:
            raise persistence_error() from exc


def make_repositories(db, transaction=None) -> Repositories:
    from app.repositories.firebase.firebase_challenge_repository import (
        FirebaseChallengeRepository,
    )
    from app.repositories.firebase.firebase_points_repository import (
        FirebasePointsRepository,
    )
    from app.repositories.firebase.firebase_report_repository import (
        FirebaseReportRepository,
    )
    from app.repositories.firebase.firebase_user_repository import (
        FirebaseUserRepository,
    )

    return Repositories(
        *(
            cls(db, transaction)
            for cls in (
                FirebaseUserRepository,
                FirebaseChallengeRepository,
                FirebaseReportRepository,
                FirebasePointsRepository,
            )
        )
    )
