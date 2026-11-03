from firebase_admin import auth
from app.exceptions.application_exceptions import ApplicationError
from app.services.common import permit
from app.config.cells import CELLS

class RegistrationService:
    def __init__(self, repositories):
        self.repos = repositories

    def list(self, actor):
        permit(actor.role in ('admin', 'evaluator') or (actor.role == 'leader' and bool(actor.ledCellIds)))
        return [{k: u.get(k) for k in ('id','name','email','role','cellId')} for u in self.repos.users.list() if actor.role in ('admin', 'evaluator') or (u.get('role') in ('student','user') and u.get('cellId') in actor.ledCellIds)]

    def cells(self, actor):
        permit(actor.role in ('admin', 'evaluator', 'leader'))
        if actor.role in ('admin', 'evaluator'):
            return CELLS
        names = {c['id']: c['name'] for c in CELLS}
        return [{'id': c, 'name': names.get(c, c)} for c in actor.ledCellIds]

    def create(self, actor, data):
        permit(actor.role in ('admin', 'evaluator') or (actor.role == 'leader' and bool(actor.ledCellIds)))
        role = data.get('role', 'student')
        permit(role in ('admin', 'student'))
        permit(role == 'student' or actor.role in ('admin', 'evaluator'))
        cell = data.get('cellId') or (actor.ledCellIds[0] if actor.role == 'leader' and len(actor.ledCellIds) == 1 else None)
        if cell not in {c['id'] for c in self.cells(actor)}:
            raise ApplicationError('INVALID_CELL', 'Selecione uma célula disponível.', 400)
        try:
            account = auth.create_user(email=data['email'], password=data['password'], display_name=data['name'])
        except auth.EmailAlreadyExistsError:
            raise ApplicationError('EMAIL_ALREADY_EXISTS', 'Já existe uma conta com este e-mail.', 409) from None
        except Exception:
            raise ApplicationError('REGISTRATION_FAILED', 'Não foi possível criar a conta no Firebase.', 502) from None
        document = {'id': account.uid, 'name': data['name'], 'email': data['email'], 'role': role, 'cellId': cell, 'level': 1, 'avatarId': 'nova'}
        if role == 'admin':
            document['ledCellIds'] = [cell]
            document['publicationTargets'] = {'GpadsTech/gpads-os-test': [f'cells/{cell}']}
        try:
            self.repos.users.create(account.uid, document)
        except Exception:
            # Compensate an incomplete registration; never store the password.
            try:
                auth.delete_user(account.uid)
            except Exception:
                raise ApplicationError('REGISTRATION_INCOMPLETE', 'Cadastro incompleto. Contate a administração para revisar a conta no Firebase.', 503) from None
            raise ApplicationError('REGISTRATION_FAILED', 'Cadastro não concluído. Tente novamente.', 503) from None
        return document
