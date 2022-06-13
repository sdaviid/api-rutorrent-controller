from datetime import date
from pydantic import Field
from datetime import datetime
from app.models.schemas.base import baseSchema


class ServerAdd(baseSchema):
    name: str
    base: str
    user: str
    password: str



class ServerDetail(baseSchema):
    id: int
    name: str
    base: str
    user: str
    password: str
    date_created: datetime
