from app.models.user import User, UserRole


def test_cell_leader_role_exists():
    leader = User(
        uid="leader_001",
        name="Líder",
        email="leader@example.com",
        role=UserRole.CELL_LEADER,
        cell_id="cell_001",
    )

    assert leader.role == UserRole.CELL_LEADER
    assert leader.cell_id == "cell_001"


def test_student_and_leader_are_distinct_roles():
    assert UserRole.STUDENT.value == "student"
    assert UserRole.CELL_LEADER.value == "cell_leader"
    assert UserRole.ADMIN.value == "admin"
