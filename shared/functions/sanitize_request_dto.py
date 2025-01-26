from pydantic import BaseModel


def sanitizeRequestData(data: BaseModel) -> dict:
    data = data.model_dump()
    data = {k: v for k, v in data.items() if v is not None}
    return data
