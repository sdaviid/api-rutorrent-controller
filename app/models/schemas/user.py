from datetime import date
from pydantic import Field
from datetime import datetime
from app.models.schemas.base import baseSchema


class UserAdd(baseSchema):
    user: str
    password: str



class UserDetail(baseSchema):
    id: int
    user: str
    password: str
    api: str
    date_created: datetime
