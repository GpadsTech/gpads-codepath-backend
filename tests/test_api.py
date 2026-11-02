from concurrent.futures import ThreadPoolExecutor

import pytest

from app.exceptions.application_exceptions import ApplicationError


def submit(client):
    response = client.post(
        "/api/reports/",
        {
            "challengeId": "ch",
            "description": "Work",
            "report": "Done",
            "code": "print(1)",
        },
        format="json",
    )
    assert response.status_code == 201, response.data
    return response.data["data"]["id"]


def approve(client, identifier, points=85):
    client.credentials(HTTP_AUTHORIZATION="Bearer leader")
    return client.post(
        f"/api/reports/{identifier}/evaluate/",
        {"points": points, "repository": "org/repo", "path": "activities/test"},
        format="json",
    )


def test_health_and_auth(client):
    assert client.get("/api/health/").json() == {
        "status": "ok",
        "message": "GPADS Backend está funcionando!",
    }
    assert client.get("/api/auth/me/").data["data"]["id"] == "s1"
    for header in ("", "Bearer invalid", "Basic s1", "Bearer s1 extra"):
        client.credentials(HTTP_AUTHORIZATION=header)
        response = client.get("/api/dashboard/")
        assert response.status_code == 401
        assert not response.data["success"]


def test_users_and_challenges(client):
    assert client.get("/api/users/s2/").status_code == 403
    assert (
        client.patch("/api/users/s1/", {"name": "New"}, format="json").status_code
        == 200
    )
    for field in ("role", "points", "level", "cellId", "ledCellIds"):
        assert (
            client.patch("/api/users/s1/", {field: 100}, format="json").status_code
            == 400
        )
    assert client.get("/api/challenges/").status_code == 200
    payload = {"title": "New task", "description": "Implement"}
    assert client.post("/api/challenges/", payload, format="json").status_code == 403
    client.credentials(HTTP_AUTHORIZATION="Bearer admin")
    response = client.post("/api/challenges/", payload, format="json")
    assert response.status_code == 201
    identifier = response.data["data"]["id"]
    assert (
        client.patch(
            f"/api/challenges/{identifier}/", {"title": "Changed"}, format="json"
        ).status_code
        == 200
    )
    assert (
        client.delete(f"/api/challenges/{identifier}/").data["data"]["status"]
        == "inactive"
    )
    assert client.get("/api/challenges/missing/").status_code == 404


@pytest.mark.parametrize("score", [0, 85, 100])
def test_complete_flow(client, system, score):
    store, publisher, _container, _actors = system
    identifier = submit(client)
    response = approve(client, identifier, score)
    assert response.status_code == 200, response.data
    assert response.data["data"]["github"]["status"] == "COMPLETED"
    assert response.data["data"]["evaluation"]["evaluatedBy"] == "leader"
    assert len(store.data["points"]) == 1
    assert len(publisher.files) == 2
    assert approve(client, identifier).status_code == 409
    calls = publisher.calls
    assert (
        client.post(
            f"/api/reports/{identifier}/publish/", {}, format="json"
        ).status_code
        == 200
    )
    assert publisher.calls == calls
    client.credentials(HTTP_AUTHORIZATION="Bearer s1")
    dashboard = client.get("/api/dashboard/").data["data"]
    assert dashboard["points"] == score and dashboard["level"] == 2
    assert dashboard["evaluatedReports"] == 1 and dashboard["progress"] == 100
    assert client.get("/api/users/s1/points/").data["data"]["total"] == score
    assert len(client.get("/api/users/s1/points/history/").data["data"]) == 1
    assert client.get("/api/ranking/me/").data["data"]["points"] == score


@pytest.mark.parametrize("score", [-1, 101, 1.5, True, "85", None])
def test_invalid_points(client, system, score):
    identifier = submit(client)
    assert approve(client, identifier, score).status_code == 400
    assert system[0].data["points"] == {}


def test_rejection_resubmission(client, system):
    identifier = submit(client)
    client.credentials(HTTP_AUTHORIZATION="Bearer leader")
    response = client.post(
        f"/api/reports/{identifier}/evaluate/",
        {"decision": "reject", "feedback": "Fix tests"},
        format="json",
    )
    assert response.data["data"]["status"] == "REJECTED"
    assert not system[0].data["points"]
    client.credentials(HTTP_AUTHORIZATION="Bearer s1")
    response = client.post(
        f"/api/reports/{identifier}/resubmit/",
        {"description": "Fixed", "code": "pass"},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["data"]["history"][0]["report"] == "Done"
    assert response.data["data"]["revision"] == 2
    assert approve(client, identifier).status_code == 200


def test_scope_and_forgery(client, system):
    identifier = submit(client)
    assert (
        client.post(
            "/api/reports/",
            {"challengeId": "ch", "description": "x", "report": "x", "studentId": "s2"},
            format="json",
        ).status_code
        == 400
    )
    for uid in ("s2", "admin"):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {uid}")
        assert client.get(f"/api/reports/{identifier}/").status_code == 403
        assert client.get("/api/reports/pending/").data["data"] == []
        assert (
            client.post(
                f"/api/reports/{identifier}/evaluate/",
                {"points": 10, "repository": "org/repo", "path": "activities/x"},
                format="json",
            ).status_code
            == 403
        )
    client.credentials(HTTP_AUTHORIZATION="Bearer leader")
    assert len(client.get("/api/reports/pending/").data["data"]) == 1
    assert client.get("/api/users/s1/").status_code == 200
    assert client.get("/api/users/s2/points/").status_code == 403


@pytest.mark.parametrize(
    "path",
    [
        "../x",
        "/activities",
        "activities/../x",
        "activities\\x",
        "activities/%2e%2e/x",
        ".github/workflows",
        "activities-evil",
    ],
)
def test_bad_github_paths(client, path):
    identifier = submit(client)
    client.credentials(HTTP_AUTHORIZATION="Bearer leader")
    response = client.post(
        f"/api/reports/{identifier}/evaluate/",
        {"points": 1, "repository": "org/repo", "path": path},
        format="json",
    )
    assert response.status_code in (400, 403)


def test_github_failure_and_retry(client, system):
    identifier = submit(client)
    system[1].fail = True
    response = approve(client, identifier)
    assert response.data["data"]["github"]["status"] == "GITHUB_ERROR"
    assert len(system[0].data["points"]) == 1
    system[1].fail = False
    assert (
        client.post(f"/api/reports/{identifier}/publish/", {}, format="json").data[
            "data"
        ]["github"]["status"]
        == "COMPLETED"
    )
    assert len(system[0].data["points"]) == 1


def test_concurrent_evaluation(client, system):
    identifier = submit(client)
    container, leader = system[2], system[3]["leader"]

    def evaluate(_):
        try:
            container.evaluations.evaluate(
                leader,
                identifier,
                {
                    "decision": "approve",
                    "feedback": "",
                    "points": 25,
                    "repository": "org/repo",
                    "path": "activities/x",
                },
            )
            return 200
        except ApplicationError as exc:
            return exc.status

    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(evaluate, range(8)))
    assert statuses.count(200) == 1 and statuses.count(409) == 7
    assert len(system[0].data["points"]) == 1


def test_persistence_rollback(client, system):
    identifier = submit(client)
    system[0].fail = True
    response = approve(client, identifier)
    assert response.status_code == 500
    assert "private" not in str(response.data)
    assert system[0].data["reports"][identifier]["status"] == "PENDING_EVALUATION"
    assert not system[0].data["points"]


def test_ranking_ties(client):
    rows = client.get("/api/ranking/").data["data"]
    assert [r["userId"] for r in rows] == ["s1", "s2"]
    assert [r["position"] for r in rows] == [1, 1]
    assert client.get("/api/ranking/?period=week").status_code == 200
    assert client.get("/api/ranking/?period=invalid").status_code == 400


def test_missing_and_empty(client):
    assert client.get("/api/reports/absent/").status_code == 404
    assert (
        client.post(
            "/api/reports/", {"challengeId": "ch", "description": "x"}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/reports/",
            {"challengeId": "absent", "description": "x", "report": "x"},
            format="json",
        ).status_code
        == 404
    )


def test_publication_lease_recovery(client, system):
    identifier = submit(client)
    system[1].fail = True
    approve(client, identifier)
    document = system[0].data["reports"][identifier]
    document["github"].update(
        status="PROCESSING", leaseId="old", leaseUntil="2999-01-01T00:00:00Z"
    )
    assert (
        client.post(
            f"/api/reports/{identifier}/publish/", {}, format="json"
        ).status_code
        == 409
    )
    system[0].data["reports"][identifier]["github"]["leaseUntil"] = (
        "2000-01-01T00:00:00Z"
    )
    system[1].fail = False
    assert (
        client.post(f"/api/reports/{identifier}/publish/", {}, format="json").data[
            "data"
        ]["github"]["status"]
        == "COMPLETED"
    )


def test_publication_checkpoint_after_remote_success(client, system, monkeypatch):
    identifier = submit(client)
    github = system[2].github
    original = github._finish

    def crash(identifier, lease, status, **data):
        if status == "COMPLETED":
            raise RuntimeError("simulated lost connection")
        return original(identifier, lease, status, **data)

    monkeypatch.setattr(github, "_finish", crash)
    assert approve(client, identifier).status_code == 500
    assert (
        system[0].data["reports"][identifier]["github"]["status"] == "GITHUB_PUBLISHED"
    )
    assert len(system[0].data["points"]) == 1
    monkeypatch.setattr(github, "_finish", original)
    calls = system[1].calls
    assert (
        client.post(f"/api/reports/{identifier}/publish/", {}, format="json").data[
            "data"
        ]["github"]["status"]
        == "COMPLETED"
    )
    assert system[1].calls == calls


def test_unauthorized_repository_and_revoked_leadership(client, system):
    identifier = submit(client)
    client.credentials(HTTP_AUTHORIZATION="Bearer leader")
    body = {"points": 80, "repository": "other/repo", "path": "activities/x"}
    assert (
        client.post(
            f"/api/reports/{identifier}/evaluate/", body, format="json"
        ).status_code
        == 403
    )
    system[0].data["users"]["leader"]["ledCellIds"] = []
    assert approve(client, identifier).status_code == 403
    assert not system[0].data["points"]


def test_inactive_challenge_and_foreign_resubmit(client, system):
    identifier = submit(client)
    system[0].data["challenges"]["ch"]["status"] = "inactive"
    assert (
        client.post(
            "/api/reports/",
            {"challengeId": "ch", "description": "x", "report": "x"},
            format="json",
        ).status_code
        == 409
    )
    client.credentials(HTTP_AUTHORIZATION="Bearer s2")
    assert (
        client.post(
            f"/api/reports/{identifier}/resubmit/",
            {"description": "x", "report": "x"},
            format="json",
        ).status_code
        == 403
    )


def test_report_size_limit(client):
    response = client.post(
        "/api/reports/",
        {
            "challengeId": "ch",
            "description": "x",
            "report": "😀" * 150000,
            "code": "😀" * 150000,
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.data["error"]["code"] == "REPORT_TOO_LARGE"


def test_self_evaluation_even_with_leader_role(client, system):
    identifier = submit(client)
    system[0].data["users"]["s1"].update(
        role="leader",
        ledCellIds=["c1"],
        publicationTargets={"org/repo": ["activities"]},
    )
    response = client.post(
        f"/api/reports/{identifier}/evaluate/",
        {"points": 50, "repository": "org/repo", "path": "activities/x"},
        format="json",
    )
    assert response.status_code == 403


def test_concurrent_publication_is_claimed_once(client, system, monkeypatch):
    from threading import Event

    identifier = submit(client)
    system[1].fail = True
    approve(client, identifier)
    system[1].fail = False
    started, release = Event(), Event()
    original = system[1].publish

    def slow_publish(repository, files):
        started.set()
        assert release.wait(5)
        return original(repository, files)

    monkeypatch.setattr(system[1], "publish", slow_publish)

    def publish():
        return system[2].github.publish(system[3]["leader"], identifier)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(publish)
        assert started.wait(5)
        try:
            with pytest.raises(ApplicationError) as error:
                publish()
            assert error.value.code == "PUBLICATION_BUSY"
        finally:
            release.set()
        assert first.result()["github"]["status"] == "COMPLETED"
    assert len(system[0].data["points"]) == 1
