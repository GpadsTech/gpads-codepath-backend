from datetime import UTC, datetime

from app.exceptions.application_exceptions import ApplicationError
from app.models.user import User


def now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def require(value, code="NOT_FOUND"):
    if value is None:
        raise ApplicationError(code, "Recurso não encontrado.", 404)
    return value


def permit(condition: bool):
    if not condition:
        raise ApplicationError("FORBIDDEN", "Acesso não autorizado.", 403)


def conflict(condition: bool, code="STATE_CONFLICT"):
    if condition:
        raise ApplicationError(code, "A operação conflita com o estado atual.", 409)


def leads(actor: User, cell_id: str | None) -> bool:
    return (
        actor.role in ("leader", "evaluator", "admin")
        and bool(cell_id)
        and cell_id in actor.ledCellIds
    )


def can_read(actor: User, report: dict) -> bool:
    return actor.id == report["studentId"] or leads(actor, report.get("cellId"))
