from pydantic import BaseModel


class HTTPExceptionResponse(BaseModel):
    detail: str


def create_http_exception_response(status_code: int, description: str):
    return {
        status_code: {
            "model": HTTPExceptionResponse,
            "description": description,
        },
    }
