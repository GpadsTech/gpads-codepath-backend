from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler


class ApplicationError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


def exception_handler(exc, context):
    if isinstance(exc, ApplicationError):
        code, message, status = exc.code, exc.message, exc.status
    else:
        response = drf_handler(exc, context)
        if response is None:
            code, message, status = (
                "INTERNAL_ERROR",
                "Não foi possível concluir a operação.",
                500,
            )
        else:
            status = response.status_code
            code = {
                400: "INVALID_INPUT",
                401: "INVALID_TOKEN",
                403: "FORBIDDEN",
                404: "NOT_FOUND",
                405: "METHOD_NOT_ALLOWED",
                413: "PAYLOAD_TOO_LARGE",
            }.get(status, "REQUEST_ERROR")
            message = {
                400: "Revise os campos e formatos enviados.",
                401: "Token ausente ou inválido.",
                403: "Acesso não autorizado.",
            }.get(status, "Requisição não permitida.")
    result = Response(
        {"success": False, "error": {"code": code, "message": message}}, status=status
    )
    if status == 401:
        result["WWW-Authenticate"] = "Bearer"
    return result
