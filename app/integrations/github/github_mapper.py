class GitHubMapper:
    """Immutable report-specific paths avoid overwriting other submissions."""

    def files(self, report: dict) -> dict[str, bytes]:
        base = f"{report['github']['path']}/{report['studentId']}/{report['id']}"
        files = {}
        if report["report"]:
            date = report.get("reportDate") or report["submittedAt"][:10]
            header = f"# Relatório quinzenal - {date}\n\nEstudante: {report['studentId']}\nData de construção: {date}\nEnviado em: {report['submittedAt']}\n\n"
            files[f"{base}/report.md"] = (header + report["report"]).encode("utf-8")
        if report["code"]:
            files[f"{base}/code.txt"] = report["code"].encode("utf-8")
        return files
