from pydantic import BaseModel
from typing import Optional


class SuccessResponseDto(BaseModel):
    data:Optional[object] = {}
    message: Optional[str] = 'درخواست انجام شد'