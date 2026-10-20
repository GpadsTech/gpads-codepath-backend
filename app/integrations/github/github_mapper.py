class GitHubMapper:
    """Immutable report-specific paths avoid overwriting other submissions."""

    def files(self, report: dict) -> dict[str, bytes]:
        base = f"{report['github']['path']}/{report['studentId']}/{report['id']}"
        files = {}
        if report["report"]:
            files[f"{base}/report.md"] = report["report"].encode("utf-8")
        if report["code"]:
            files[f"{base}/code.txt"] = report["code"].encode("utf-8")
        return files
