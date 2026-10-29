from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
from app.exceptions.application_exceptions import ApplicationError
from app.integrations.github.github_mapper import GitHubMapper


def configure(system, monkeypatch):
    store, publisher, container, actors = system
    monkeypatch.setenv('GEMINI_API_KEY', 'offline-test-key')
    session = Mock()
    session.post.return_value.status_code = 200
    session.post.return_value.json.return_value = {'candidates': [{'content': {'parts': [{'text': '# Relatório de teste'}]}}]}
    container.ai.session = session
    return store, container.ai, session, actors


def test_ai_two_requests_then_blocked(system, monkeypatch):
    store, ai, session, actors = configure(system, monkeypatch)
    assert ai.generate(actors['s1'], {'activities': 'Estudei Django'})['usage']['remaining'] == 1
    assert ai.generate(actors['s1'], {'activities': 'Criei rotas'})['usage']['remaining'] == 0
    with pytest.raises(ApplicationError) as error:
        ai.generate(actors['s1'], {'activities': 'Terceira'})
    assert error.value.status == 429
    assert session.post.call_count == 2
    assert ai.usage(actors['s2'])['remaining'] == 2
    store.repos.users.patch('s1', {'aiUsage': {'date': '2000-01-01', 'count': 2}})
    assert ai.usage(actors['s1'])['remaining'] == 2


def test_ai_parallel_reservations(system, monkeypatch):
    store, ai, session, actors = configure(system, monkeypatch)
    def call(_):
        try:
            ai.generate(actors['s1'], {'activities': 'Código'})
            return True
        except ApplicationError:
            return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(call, range(8))) == 2
    assert session.post.call_count == 2


def test_ai_failure_consumes_attempt_without_retry_or_secret(system, monkeypatch):
    store, ai, session, actors = configure(system, monkeypatch)
    session.post.side_effect = requests.Timeout('secret-key')
    with pytest.raises(ApplicationError) as error:
        ai.generate(actors['s1'], {'activities': 'Código'})
    assert 'secret-key' not in str(error.value)
    assert ai.usage(actors['s1'])['used'] == 1
    assert session.post.call_count == 1
    with pytest.raises(ApplicationError) as error:
        ai.generate(actors['leader'], {'activities': 'Código'})
    assert error.value.status == 403


def test_registration_exclusive_leader_and_password_not_stored(system, monkeypatch):
    store, _, container, actors = system
    create = Mock(return_value=SimpleNamespace(uid='new-student'))
    monkeypatch.setattr('app.services.registration_service.auth.create_user', create)
    data = {'name': 'Novo membro', 'email': 'new@example.test', 'password': 'strong-pass-123', 'role': 'student'}
    for role in ['s1', 's2', 'admin']:
        with pytest.raises(ApplicationError):
            container.registration.create(actors[role], data)
    create.assert_not_called()
    user = container.registration.create(actors['leader'], data)
    assert user['cellId'] == 'c1' and user['role'] == 'student'
    assert 'password' not in user and 'password' not in store.repos.users.get(user['id'])
    assert len(container.registration.list(actors['leader'])) == 2


def test_registration_compensates_profile_failure(system, monkeypatch):
    store, _, container, actors = system
    monkeypatch.setattr('app.services.registration_service.auth.create_user', Mock(return_value=SimpleNamespace(uid='new')))
    delete = Mock()
    monkeypatch.setattr('app.services.registration_service.auth.delete_user', delete)
    monkeypatch.setattr(store.repos.users, 'create', Mock(side_effect=RuntimeError('private')))
    with pytest.raises(ApplicationError):
        container.registration.create(actors['leader'], {'name': 'N', 'email': 'n@example.test', 'password': 'password', 'role': 'student'})
    delete.assert_called_once_with('new')


def test_avatar_and_registration_api_guards(client):
    assert client.patch('/api/users/s1/', {'avatarId': 'atlas'}, format='json').data['data']['avatarId'] == 'atlas'
    assert client.patch('/api/users/s1/', {'avatarId': 'invalid'}, format='json').status_code == 400
    assert client.post('/api/students/', {'name':'N','email':'n@example.test','password':'password123','role':'student'}, format='json').status_code == 403
    client.credentials(HTTP_AUTHORIZATION='Bearer leader')
    assert client.post('/api/students/', {'name':'N','email':'n@example.test','password':'password123','role':'leader'}, format='json').status_code == 400


def test_report_date_in_student_folder():
    report = {'github': {'path': 'relatorios/celula'}, 'studentId': 's1', 'id': 'r1', 'submittedAt': '2026-10-29T12:00:00Z', 'reportDate': '2026-10-28', 'report': 'Minha quinzena', 'code': ''}
    files = GitHubMapper().files(report)
    assert 'relatorios/celula/s1/r1/report.md' in files
    assert 'Data de construção: 2026-10-28' in next(iter(files.values())).decode()
