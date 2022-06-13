from pydantic import BaseModel


class baseSchema(BaseModel):
    class Config:
        orm_mode = True