from abc import ABC, abstractmethod
from typing import Optional


class GitHubClient(ABC):
    """
    Contrato técnico para a API do GitHub.

    A implementação concreta será criada na Sprint 2.
    Nenhum token, OAuth ou chamada HTTP deve ser colocado aqui agora.
    """

    @abstractmethod
    def publish_file(
        self,
        repository: str,
        path: str,
        content: str,
        message: str,
    ) -> str:
        """
        Publica um arquivo e retorna uma referência da publicação,
        por exemplo a URL ou SHA retornada pelo GitHub.
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError
