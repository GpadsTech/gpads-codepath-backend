from app.models.report import Report


def build_report_content(report: Report) -> str:
    """
    Converte uma entrega em conteúdo publicável no GitHub.

    A regra de negócio não fica aqui; este módulo apenas transforma
    dados internos em conteúdo para a integração externa.
    """
    sections = [
        f"# Entrega {report.id}",
        f"Estudante: {report.student_id}",
        f"Atividade: {report.challenge_id}",
        "",
        "## Descrição",
        report.description,
    ]

    if report.report:
        sections.extend(["", "## Relatório", report.report])

    if report.code:
        sections.extend(["", "## Código", "```text", report.code, "```"])

    return "\n".join(sections)
