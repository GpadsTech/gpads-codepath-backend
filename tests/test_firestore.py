"""Opt-in emulator smoke test. Never loads service-account credentials."""

import os
from uuid import uuid4

import pytest


@pytest.mark.emulator
@pytest.mark.skipif(
    os.getenv("RUN_FIRESTORE_EMULATOR_TESTS") != "1",
    reason="Local emulator not requested",
)
def test_emulator_atomic_write_and_read():
    from google.auth.credentials import AnonymousCredentials
    from google.cloud.firestore import Client

    from app.repositories.firebase.base import FirebaseUnitOfWork, make_repositories

    host = os.environ.get("FIRESTORE_EMULATOR_HOST", "")
    assert host.startswith(("127.0.0.1:", "localhost:")), (
        "Only loopback emulator permitted"
    )
    db = Client(project="demo-codepath-tests", credentials=AnonymousCredentials())
    identifier = "test_" + uuid4().hex
    repos = make_repositories(db)
    try:

        def operation(transaction_repos):
            assert transaction_repos.reports.get(identifier) is None
            assert transaction_repos.points.get(identifier) is None
            transaction_repos.reports.create(identifier, {"status": "EVALUATED"})
            transaction_repos.points.create(identifier, {"points": 0})

        FirebaseUnitOfWork(db).run(operation)
        assert repos.reports.get(identifier)["status"] == "EVALUATED"
        assert repos.points.get(identifier)["points"] == 0
    finally:
        db.collection("reports").document(identifier).delete()
        db.collection("points").document(identifier).delete()
        db.close()
