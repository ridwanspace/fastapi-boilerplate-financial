from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorItem(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorItem]
