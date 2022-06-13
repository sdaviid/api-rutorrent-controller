from sqlalchemy import(
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.types import(
    Date,
    Boolean,
    Time,
    DateTime
)
from sqlalchemy.orm import(
    relationship,
    backref
)
from app.models.base import ModelBase
from app.core.database import Base
from datetime import datetime

from utils.encode import(
    gen_random_md5
)


class User(ModelBase, Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user = Column(String(255))
    password = Column(String(255))
    api = Column(String(255))
    date_created = Column(DateTime, default=datetime.utcnow())


    @classmethod
    def add(cls, session, data):
        user = User()
        user.user = data.user
        user.password = data.password
        user.api = gen_random_md5()
        session.add(user)
        session.commit()
        session.refresh(user)
        return User.find_by_id(session=session, id=user.id)




