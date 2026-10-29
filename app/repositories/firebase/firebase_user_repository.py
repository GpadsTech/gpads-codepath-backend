from app.repositories.firebase.base import FirebaseDocumentRepository


class FirebaseUserRepository(FirebaseDocumentRepository):
    def __init__(self, db, transaction=None):
        super().__init__(db, "users", transaction)
