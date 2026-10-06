from app.integrations.github.github_mapper import build_report_content
from app.models.report import Report
from app.repositories.interfaces.points_repository import PointsRepository
from app.repositories.interfaces.reports_repository import ReportRepository


def test_report_repository_contract_exists():
    assert hasattr(ReportRepository, "create")
    assert hasattr(ReportRepository, "find_by_id")
    assert hasattr(ReportRepository, "list_all")
    assert hasattr(ReportRepository, "list_by_status")
    assert hasattr(ReportRepository, "update")


def test_points_repository_contract_exists():
    assert hasattr(PointsRepository, "create")
    assert hasattr(PointsRepository, "find_by_submission")
    assert hasattr(PointsRepository, "find_by_student")
    assert hasattr(PointsRepository, "find_history")
    assert hasattr(PointsRepository, "total_by_student")


def test_github_mapper_contains_delivery_information():
    report = Report(
        id="report_001",
        student_id="uid_001",
        challenge_id="activity_001",
        description="Minha entrega",
        report="Relatório",
        code="print('hello')",
    )

    content = build_report_content(report)

    assert "report_001" in content
    assert "uid_001" in content
    assert "activity_001" in content
    assert "Relatório" in content
    assert "print('hello')" in content
