from app.repositories.firebase.base import FirebaseDocumentRepository


class FirebasePointsRepository(FirebaseDocumentRepository):
    def __init__(self, db, transaction=None):
        super().__init__(db, "points", transaction)
