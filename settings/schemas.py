from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_valid: bool
    value: str
