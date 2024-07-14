class BaseException(Exception):
    def __init__(self, body):
        self.body = body


class NotFound(BaseException):
    status_code = 404
    message = "Not Found"


class Forbidden(BaseException):
    status_code = 403
    message = "Forbidden"


class BadRequest(BaseException):
    status_code = 400
    message = "Bad Request"
