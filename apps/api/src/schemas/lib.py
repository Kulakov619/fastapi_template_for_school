from uuid import UUID

from pydantic import BaseModel


class Author(BaseModel):
    id: int
    first_name: str
    last_name: str


class Authors(BaseModel):
    authors: list[Author]


class AuthorCreate(BaseModel):
    first_name: str
    last_name: str
