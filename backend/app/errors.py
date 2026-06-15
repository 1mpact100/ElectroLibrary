class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message


class EntityNotFoundError(AppError):
    status_code = 404
    code = "ENTITY_NOT_FOUND"


class DuplicateEntityError(AppError):
    status_code = 409
    code = "DUPLICATE_ENTITY"


class EntityInUseError(AppError):
    status_code = 409
    code = "ENTITY_IN_USE"


class RevisionConflictError(AppError):
    status_code = 409
    code = "REVISION_CONFLICT"


class DatabaseRequestError(AppError):
    status_code = 400
    code = "DATABASE_REQUEST_ERROR"


class DatabaseUnavailableError(AppError):
    status_code = 503
    code = "DATABASE_UNAVAILABLE"
