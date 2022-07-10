from datetime import date
from pydantic import Field
from datetime import datetime
from app.models.schemas.base import baseSchema


class FileAdd(baseSchema):
    source_id: int
    name: str
    serve_uri: str 
    



class FileDetail(baseSchema):
    id: int
    source_id: int
    name: str
    serve_uri: str
    status: str
    serve_uploaded: str
    date_created: datetime
    