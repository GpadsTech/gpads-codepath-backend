from typing import Protocol

from rest_framework.exceptions import AuthenticationFailed

from app.models.user import User
from app.repositories.interfaces.user_repository import UserRepository


class TokenVerifier(Protocol):
    def verify(self, token: str) -> dict: ...


class AuthService:
    def __init__(self, verifier: TokenVerifier, users: UserRepository):
        self.verifier, self.users = verifier, users

    def authenticate(self, token: str) -> User:
        claims = self.verifier.verify(token)
        document = self.users.get(claims["uid"])
        if not document:
            raise AuthenticationFailed("Perfil não provisionado.")
        return User.from_document(document)
