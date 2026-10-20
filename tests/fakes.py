from copy import deepcopy
from threading import RLock

from app.integrations.github.github_client import GitHubFailure
from app.repositories.interfaces.repositories import Repositories


class MemoryRepository:
    def __init__(self, store, name):
        self.store, self.name = store, name

    def get(self, identifier):
        return deepcopy(self.store.data[self.name].get(identifier))

    def list(self):
        return deepcopy(list(self.store.data[self.name].values()))

    def create(self, identifier, data):
        assert identifier not in self.store.data[self.name]
        self.store.data[self.name][identifier] = deepcopy(data)

    def patch(self, identifier, data):
        self.store.data[self.name][identifier].update(deepcopy(data))


class MemoryUnitOfWork:
    def __init__(self):
        self.data = {name: {} for name in ("users", "challenges", "reports", "points")}
        self.lock = RLock()
        self.repos = Repositories(*(MemoryRepository(self, name) for name in self.data))
        self.fail = False

    def run(self, operation):
        with self.lock:
            old = deepcopy(self.data)
            try:
                result = operation(self.repos)
                if self.fail:
                    raise RuntimeError("private storage details")
                return result
            except Exception:
                self.data = old
                raise


class Publisher:
    def __init__(self):
        self.fail = False
        self.files = {}
        self.calls = 0

    def publish(self, repository, files):
        self.calls += 1
        if self.fail:
            raise GitHubFailure("GITHUB_NETWORK")
        self.files.update(files)
        return [
            {"path": path, "sha": "test-sha", "url": "https://github.com/org/repo"}
            for path in files
        ]
