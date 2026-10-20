import os
from pathlib import Path
from threading import Lock

import firebase_admin
from firebase_admin import credentials, firestore


class FirebaseConfig:
    """Lazy Admin SDK initialization; importing Django never connects to Firebase."""

    _lock = Lock()

    def initialize(self):
        with self._lock:
            try:
                firebase_admin.get_app()
            except ValueError:
                path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                credential = None
                if path:
                    path = Path(path)
                    if not path.is_absolute():
                        path = Path(__file__).resolve().parents[2] / path
                    credential = credentials.Certificate(str(path))
                options = (
                    {"projectId": os.environ["FIREBASE_PROJECT_ID"]}
                    if os.getenv("FIREBASE_PROJECT_ID")
                    else None
                )
                firebase_admin.initialize_app(credential, options)
        return firestore.client()

    @property
    def firestore(self):
        return self.initialize()
