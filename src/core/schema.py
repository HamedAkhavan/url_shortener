from pydantic import BaseModel


class BasicMessage(BaseModel):
    detail: str
    meta: dict = {}
