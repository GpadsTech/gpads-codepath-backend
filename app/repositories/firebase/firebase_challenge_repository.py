from app.repositories.firebase.base import FirebaseDocumentRepository


class FirebaseChallengeRepository(FirebaseDocumentRepository):
    def __init__(self, db, transaction=None):
        super().__init__(db, "challenges", transaction)
