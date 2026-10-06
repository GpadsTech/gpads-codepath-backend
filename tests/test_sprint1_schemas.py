import pytest
from pydantic import ValidationError

from app.schemas.report_schema import (
    EvaluationRequestSchema,
    ReportCreateSchema,
)


def test_report_requires_report_or_code():
    with pytest.raises(ValidationError):
        ReportCreateSchema(
            student_id="uid_001",
            challenge_id="activity_001",
            description="Entrega",
        )


def test_report_accepts_report_only():
    data = ReportCreateSchema(
        student_id="uid_001",
        challenge_id="activity_001",
        description="Entrega",
        report="Meu relatório",
    )

    assert data.report == "Meu relatório"
    assert data.code is None


def test_report_accepts_code_only():
    data = ReportCreateSchema(
        student_id="uid_001",
        challenge_id="activity_001",
        description="Entrega",
        code="print('hello')",
    )

    assert data.code == "print('hello')"


@pytest.mark.parametrize("points", [-1, 101])
def test_evaluation_rejects_invalid_points(points):
    with pytest.raises(ValidationError):
        EvaluationRequestSchema(
            points=points,
            repository="gpads-dashboard",
            path="atividades/ranking/joao/",
        )


def test_evaluation_accepts_zero_points():
    data = EvaluationRequestSchema(
        points=0,
        repository="gpads-dashboard",
        path="atividades/ranking/joao/",
    )

    assert data.points == 0


def test_evaluation_accepts_maximum_points():
    data = EvaluationRequestSchema(
        points=100,
        repository="gpads-dashboard",
        path="atividades/ranking/joao/",
    )

    assert data.points == 100
