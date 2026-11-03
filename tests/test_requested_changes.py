from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.config.cells import CELLS
from app.exceptions.application_exceptions import ApplicationError
from app.integrations.github.github_mapper import GitHubMapper
from app.models.user import User


@pytest.mark.parametrize('role', ['admin', 'evaluator'])
@pytest.mark.parametrize('new_role', ['admin', 'student'])
def test_managers_register_both_roles(system, monkeypatch, role, new_role):
    store, _, container, _ = system
    actor = User(id='manager', role=role)
    monkeypatch.setattr('app.services.registration_service.auth.create_user', Mock(return_value=SimpleNamespace(uid='new')))
    data = dict(name='Nathália', email='n@example.test', password='password123', role=new_role, cellId='hardware')
    result = container.registration.create(actor, data)
    assert result['role'] == new_role
    assert result['cellId'] == 'hardware'
    assert 'password' not in store.repos.users.get('new')
    if new_role == 'admin':
        assert result['ledCellIds'] == ['hardware']
    assert len(container.registration.cells(actor)) == 7


def test_registration_rejects_unknown_cell_and_leader_escalation(system, monkeypatch):
    _, _, container, actors = system
    create = Mock()
    monkeypatch.setattr('app.services.registration_service.auth.create_user', create)
    for actor, role, cell in [(actors['admin'], 'student', 'fake-cell'), (actors['leader'], 'admin', 'c1'), (actors['s1'], 'student', 'hardware')]:
        with pytest.raises(ApplicationError):
            container.registration.create(actor, dict(name='N', email='n@example.test', password='password123', role=role, cellId=cell))
    create.assert_not_called()


def test_catalog_endpoint_and_new_avatars(client):
    assert client.get('/api/cells/').status_code == 403
    for avatar in ('leo', 'kai', 'theo', 'dante', 'iris', 'maya'):
        assert client.patch('/api/users/s1/', {'avatarId': avatar}, format='json').status_code == 200
    client.credentials(HTTP_AUTHORIZATION='Bearer admin')
    assert client.get('/api/cells/').data['data'] == CELLS


def test_readable_publication_name_uses_sao_paulo_submission_date():
    report = dict(github=dict(path='cells/hardware', layoutVersion=2, authorName='Nathália / ../ Teste'), studentId='s1', id='random-id', submittedAt='2026-11-03T01:30:00.123456Z', reportDate='2026-10-30', report='Relato', code='code')
    files = GitHubMapper().files(report)
    key = next(k for k in files if k.endswith('.md'))
    assert key.endswith('/relatorio_quinzenal_nathalia_teste_02_11_2026.md')
    assert 'random-id' not in key and '..' not in key
    assert 'Data de construção: 2026-10-30' in files[key].decode()
    assert GitHubMapper().files(report) == files
    report['submittedAt'] = '2026-11-03T01:31:00.123456Z'
    assert not set(files).intersection(GitHubMapper().files(report))
