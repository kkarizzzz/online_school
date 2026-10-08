"""
Ошибки сервисного слоя. main.py превращает их в HTTP-ответ {"detail": "<текст>"}
с кодом status_code, поэтому в роутерах их не нужно ловить.
"""


class ServiceError(Exception):
    status_code = 400

    @property
    def detail(self) -> str:
        return str(self.args[0]) if self.args else 'Некорректный запрос'


class NotFoundError(ServiceError):
    status_code = 404


class ConflictError(ServiceError):
    status_code = 409
