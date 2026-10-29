import base64
import hashlib
from typing import Protocol
from urllib.parse import quote

import requests


class GitHubFailure(Exception):
    """Sanitized technical failure; never contains request headers or response bodies."""


class GitHubPublisher(Protocol):
    def publish(self, repository: str, files: dict[str, bytes]) -> list[dict]: ...


class GitHubClient:
    def __init__(self, token: str, session=None):
        self.token = token
        self.session = session or requests.Session()

    def request(self, method, url, **kwargs):
        if not self.token:
            raise GitHubFailure("GITHUB_CONFIGURATION")
        try:
            response = self.session.request(
                method,
                url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=(5, 20),
                allow_redirects=False,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise GitHubFailure("GITHUB_NETWORK") from exc
        return response

    def publish(self, repository: str, files: dict[str, bytes]) -> list[dict]:
        published = []
        for path, content in files.items():
            url = f"https://api.github.com/repos/{repository}/contents/{quote(path, safe='/')}"
            expected = hashlib.sha1(
                b"blob " + str(len(content)).encode() + b"\0" + content
            ).hexdigest()
            response = self.request("GET", url)
            if response.status_code == 200:
                try:
                    item = response.json()
                except ValueError as exc:
                    raise GitHubFailure("GITHUB_RESPONSE") from exc
                if not isinstance(item, dict) or item.get("sha") != expected:
                    raise GitHubFailure("GITHUB_CONTENT_CONFLICT")
            elif response.status_code == 404:
                response = self.request(
                    "PUT",
                    url,
                    json={
                        "message": "Register evaluated CodePath submission",
                        "content": base64.b64encode(content).decode(),
                    },
                )
                if response.status_code not in (200, 201):
                    raise GitHubFailure("GITHUB_WRITE_FAILED")
                try:
                    item = response.json()["content"]
                except (ValueError, KeyError, TypeError) as exc:
                    raise GitHubFailure("GITHUB_RESPONSE") from exc
                if item.get("sha") != expected:
                    raise GitHubFailure("GITHUB_CONTENT_CONFLICT")
            else:
                raise GitHubFailure("GITHUB_READ_FAILED")
            published.append(
                {
                    "path": path,
                    "sha": expected,
                    "url": f"https://github.com/{repository}/blob/HEAD/{quote(path, safe='/')}",
                }
            )
        return published
