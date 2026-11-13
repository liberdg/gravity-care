class ApiError(Exception):
    """Format d'erreur unique de l'API : {code, message}."""

    def __init__(self, status_code: int, code: str, message: str):
        self.status_code, self.code, self.message = status_code, code, message
