from models import HttpResponse, BAD_REQUEST
from utils import validate_input
from exceptions import BadRequest


class OperationManager:
    def __init__(self, fn_mappings: dict, input_cls_mappings: dict):
        self.fn_mappings = fn_mappings
        self.input_cls_mappings = input_cls_mappings

    def create_HTML(self, operation, parameters):
        if operation not in self.fn_mappings:
            return HttpResponse(
                status_code=404,
                response_message="Not Found",
                title="Error",
                body="Invalid Operation.",
            ).html

        operation_fn = self.fn_mappings[operation]

        if operation not in self.input_cls_mappings:
            return BAD_REQUEST.html

        input_cls = self.input_cls_mappings[operation]

        try:
            input = validate_input(input_cls, parameters)
        except BadRequest:
            return BAD_REQUEST.html

        http_response = operation_fn(input)
        return http_response.html
