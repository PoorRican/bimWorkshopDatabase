from pydantic import BaseModel


class Parameter(BaseModel):
    name: str
    values: list[str]
