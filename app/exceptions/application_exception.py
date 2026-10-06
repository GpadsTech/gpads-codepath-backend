class ApplicationError(Exception):
    """Exceção base da aplicação."""


class ReportNotFoundError(ApplicationError):
    pass


class ReportAlreadyEvaluatedError(ApplicationError):
    pass


class PermissionDeniedError(ApplicationError):
    pass


class InvalidPointsError(ApplicationError):
    pass


class GitHubPublicationError(ApplicationError):
    pass
