from datetime import datetime

from pydantic import BaseModel


class ExampleBase(BaseModel):
    type: str
    time: datetime
    code: str


class ExampleResponse(BaseModel):
    data: list[ExampleBase]
