from app.repositories.firebase.base import FirebaseDocumentRepository


class FirebaseReportRepository(FirebaseDocumentRepository):
    def __init__(self, db, transaction=None):
        super().__init__(db, "reports", transaction)
