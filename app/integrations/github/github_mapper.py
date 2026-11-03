import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo


class GitHubMapper:
    """Immutable report-specific paths avoid overwriting other submissions."""

    def files(self, report: dict) -> dict[str, bytes]:
        base = f"{report['github']['path']}/{report['studentId']}/{report['id']}"
        report_name, code_name = 'report.md', 'code.txt'
        if report['github'].get('layoutVersion') == 2:
            author = report['github']['authorName']
            slug = unicodedata.normalize('NFKD', author).encode('ascii', 'ignore').decode().lower()
            slug = re.sub(r'[^a-z0-9]+', '_', slug).strip('_')[:80] or 'estudante'
            sent = datetime.fromisoformat(report['submittedAt'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Sao_Paulo'))
            # Timestamp legível separa entregas da mesma pessoa no mesmo dia.
            # O nome é congelado na avaliação para que novas tentativas sejam idempotentes.
            base = f"{report['github']['path']}/{slug}/{sent:%Y}/{sent:%d_%m_%Y_%H%M%S_%f}"
            report_name = f'relatorio_quinzenal_{slug}_{sent:%d_%m_%Y}.md'
            code_name = f'codigo_{slug}_{sent:%d_%m_%Y}.txt'
        files = {}
        if report["report"]:
            date = report.get("reportDate") or report["submittedAt"][:10]
            header = f"# Relatório quinzenal - {date}\n\nEstudante: {report['studentId']}\nData de construção: {date}\nEnviado em: {report['submittedAt']}\n\n"
            files[f"{base}/{report_name}"] = (header + report["report"]).encode("utf-8")
        if report["code"]:
            files[f"{base}/{code_name}"] = report["code"].encode("utf-8")
        return files
