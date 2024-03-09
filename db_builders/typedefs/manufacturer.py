from pydantic import BaseModel


class Manufacturer(BaseModel):
    title: str
    url: str
