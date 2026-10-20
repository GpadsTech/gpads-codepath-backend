import base64
import hashlib
from unittest.mock import Mock

import pytest
import requests
from google.api_core.exceptions import ServiceUnavailable
from rest_framework.exceptions import AuthenticationFailed

from app.exceptions.application_exceptions import ApplicationError
from app.integrations.github.github_client import GitHubClient, GitHubFailure
from app.middleware.auth_middleware import FirebaseTokenVerifier
from app.repositories.firebase.base import FirebaseDocumentRepository


def response(status, body):
    item = Mock(status_code=status)
    item.json.return_value = body
    return item


def test_github_upload_and_safe_replay():
    content = b"hello"
    sha = hashlib.sha1(b"blob 5\0hello").hexdigest()
    session = Mock()
    session.request.side_effect = [
        response(404, {}),
        response(201, {"content": {"sha": sha}}),
        response(200, {"sha": sha}),
    ]
    github = GitHubClient("test-token", session)
    first = github.publish("org/repo", {"activities/s1/r1/report.md": content})
    assert github.publish("org/repo", {"activities/s1/r1/report.md": content}) == first
    assert session.request.call_count == 3
    payload = session.request.call_args_list[1].kwargs["json"]
    assert base64.b64decode(payload["content"]) == content
    assert session.request.call_args.kwargs["allow_redirects"] is False


@pytest.mark.parametrize("status", [401, 403, 409, 422, 500])
def test_github_http_failure(status):
    session = Mock()
    session.request.return_value = response(status, {"token": "do-not-expose"})
    with pytest.raises(GitHubFailure) as error:
        GitHubClient("secret", session).publish("org/repo", {"a": b"x"})
    assert "secret" not in str(error.value) and "do-not-expose" not in str(error.value)


def test_github_timeout_and_content_conflict():
    session = Mock()
    session.request.side_effect = requests.Timeout("secret")
    with pytest.raises(GitHubFailure, match="GITHUB_NETWORK"):
        GitHubClient("secret", session).publish("org/repo", {"a": b"x"})
    session.request.side_effect = None
    session.request.return_value = response(200, {"sha": "different"})
    with pytest.raises(GitHubFailure, match="GITHUB_CONTENT_CONFLICT"):
        GitHubClient("secret", session).publish("org/repo", {"a": b"x"})


def test_token_verifier_delegates_sdk(monkeypatch):
    verify = Mock(return_value={"uid": "s1"})
    monkeypatch.setattr("app.middleware.auth_middleware.auth.verify_id_token", verify)
    assert FirebaseTokenVerifier().verify("opaque")["uid"] == "s1"
    verify.assert_called_once_with("opaque", check_revoked=True)
    verify.side_effect = ValueError("secret")
    with pytest.raises(AuthenticationFailed):
        FirebaseTokenVerifier().verify("bad")


def test_firestore_error_is_sanitized():
    db = Mock()
    db.collection.return_value.document.return_value.get.side_effect = (
        ServiceUnavailable("private")
    )
    with pytest.raises(ApplicationError) as exc:
        FirebaseDocumentRepository(db, "users").get("x")
    assert exc.value.code == "PERSISTENCE_ERROR"
    assert "private" not in exc.value.message


def test_partial_github_publication_recovery():
    session = Mock()

    def sha(content):
        return hashlib.sha1(
            b"blob " + str(len(content)).encode() + b"\0" + content
        ).hexdigest()

    a, b = b"report", b"code"
    session.request.side_effect = [
        response(404, {}),
        response(201, {"content": {"sha": sha(a)}}),
        response(500, {}),
        response(200, {"sha": sha(a)}),
        response(404, {}),
        response(201, {"content": {"sha": sha(b)}}),
    ]
    github = GitHubClient("token", session)
    with pytest.raises(GitHubFailure):
        github.publish("org/repo", {"a": a, "b": b})
    assert len(github.publish("org/repo", {"a": a, "b": b})) == 2
    assert [c.args[0] for c in session.request.call_args_list].count("PUT") == 2


def test_firestore_transaction_read_write_contract():
    from unittest.mock import patch

    from google.cloud import firestore

    from app.repositories.firebase.base import FirebaseUnitOfWork

    db, transaction = Mock(), Mock()
    db.transaction.return_value = transaction
    snapshot = Mock(id="s1", exists=True)
    snapshot.to_dict.return_value = {"name": "A"}
    db.collection.return_value.document.return_value.get.return_value = snapshot
    with patch.object(firestore, "transactional", side_effect=lambda f: f):

        def operation(repos):
            user = repos.users.get("s1")
            repos.users.patch("s1", {"name": user["name"] + "B"})
            repos.points.create("r1", {"points": 0})
            return user

        assert FirebaseUnitOfWork(db).run(operation)["id"] == "s1"
    db.collection.return_value.document.return_value.get.assert_called_with(
        transaction=transaction
    )
    assert transaction.update.call_count == 1
    assert transaction.create.call_count == 1
