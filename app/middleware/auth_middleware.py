from firebase_admin import auth
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed


class FirebaseTokenVerifier:
    def verify(self, token: str) -> dict:
        try:
            return auth.verify_id_token(token, check_revoked=True)
        except (
            ValueError,
            auth.InvalidIdTokenError,
            auth.ExpiredIdTokenError,
            auth.RevokedIdTokenError,
            auth.UserDisabledError,
        ) as exc:
            raise AuthenticationFailed("Token inválido.") from exc


class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts:
            return None
        if len(parts) != 2 or parts[0].lower() != b"bearer":
            raise AuthenticationFailed("Cabeçalho inválido.")
        try:
            token = parts[1].decode("ascii")
        except UnicodeDecodeError as exc:
            raise AuthenticationFailed("Token inválido.") from exc
        from app.config.dependencies import get_container

        return get_container().auth.authenticate(token), None

    def authenticate_header(self, request):
        return "Bearer"
