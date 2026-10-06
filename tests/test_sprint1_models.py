import pytest

from app.models.points import Points
from app.models.report import (
    DeliveryStatus,
    Evaluation,
    GitHubPublication,
    PublicationStatus,
    Report,
)


def test_report_starts_pending_evaluation():
    report = Report(
        id="report_001",
        student_id="uid_001",
        challenge_id="activity_001",
        description="Minha entrega",
        report="Relatório",
    )

    assert report.status == DeliveryStatus.PENDING_EVALUATION
    assert report.evaluation is None
    assert report.github is None


@pytest.mark.parametrize("points", [0, 1, 50, 100])
def test_points_accepts_range(points):
    item = Points(
        student_id="uid_001",
        activity_id="activity_001",
        submission_id="report_001",
        points=points,
        evaluated_by="leader_001",
    )

    assert item.points == points


@pytest.mark.parametrize("points", [-1, 101])
def test_points_rejects_out_of_range(points):
    with pytest.raises(ValueError):
        Points(
            student_id="uid_001",
            activity_id="activity_001",
            submission_id="report_001",
            points=points,
            evaluated_by="leader_001",
        )


def test_github_statuses_are_defined():
    assert PublicationStatus.PENDING.value == "PENDING"
    assert PublicationStatus.PROCESSING.value == "PROCESSING"
    assert PublicationStatus.GITHUB_PUBLISHED.value == "GITHUB_PUBLISHED"
    assert PublicationStatus.COMPLETED.value == "COMPLETED"
    assert PublicationStatus.GITHUB_ERROR.value == "GITHUB_ERROR"


def test_rejected_is_the_returned_delivery_status():
    assert DeliveryStatus.REJECTED.value == "REJECTED"
