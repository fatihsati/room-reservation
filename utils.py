from exceptions import BadRequest


def parse_input(message: str) -> tuple[str, dict]:
    connection_method = message.split(" ")[0]  # GET or POST

    # get the url from header
    requested_url = message.split(" ")[1]
    if requested_url == "/favicon.ico":
        # example /favicon.ico message
        return False, None

    try:
        operation = requested_url.split("?")[0].split("/")[-1]

        parameters = {}
        # split the url to a dictionary where key day and value is the day number

        parameters_part = requested_url.split("?")[1]
        splitted_parameters = parameters_part.split("&")

        for key, value in [parameter.split("=") for parameter in splitted_parameters]:
            parameters[key] = value
    except:
        return None, None
    return operation, parameters


def validate_input(cls, params):
    try:
        input = cls(**params)
    except:
        raise BadRequest(body="Invalid Input.")
    return input
