from unittest.mock import Mock

import pytest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIClient

from app.config.dependencies import Container
from app.models.user import User
from tests.fakes import MemoryUnitOfWork, Publisher


@pytest.fixture(autouse=True)
def forbid_external(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("External access forbidden in offline tests")

    monkeypatch.setattr("requests.sessions.Session.request", fail)
    monkeypatch.setattr("app.config.firebase.FirebaseConfig.initialize", fail)


@pytest.fixture
def system(monkeypatch):
    store, publisher = MemoryUnitOfWork(), Publisher()
    docs = [
        {
            "id": "s1",
            "name": "Ana",
            "email": "ana@example.test",
            "role": "student",
            "cellId": "c1",
            "level": 2,
        },
        {"id": "s2", "name": "Bia", "role": "user", "cellId": "c2"},
        {
            "id": "leader",
            "role": "leader",
            "ledCellIds": ["c1"],
            "publicationTargets": {"org/repo": ["activities"]},
        },
        {"id": "admin", "role": "admin"},
    ]
    for doc in docs:
        store.repos.users.create(doc["id"], doc)
    store.repos.challenges.create(
        "ch",
        {
            "id": "ch",
            "title": "Task",
            "description": "Task",
            "status": "active",
            "cellId": "c1",
        },
    )
    verifier = Mock()

    def verify(token):
        if token not in store.data["users"]:
            raise AuthenticationFailed("Invalid")
        return {"uid": token}

    verifier.verify.side_effect = verify
    container = Container(store.repos, store, verifier, publisher, {"org/repo"})
    monkeypatch.setattr("app.config.dependencies.get_container", lambda: container)
    monkeypatch.setattr("app.controllers.base.get_container", lambda: container)
    return store, publisher, container, {d["id"]: User.from_document(d) for d in docs}


@pytest.fixture
def client(system):
    api = APIClient()
    api.credentials(HTTP_AUTHORIZATION="Bearer s1")
    return api
