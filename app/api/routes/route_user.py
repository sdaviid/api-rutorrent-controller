from typing import List
from sqlalchemy.orm import Session
from fastapi import(
    Depends,
    Response,
    status,
    APIRouter
)

from fastapi.responses import JSONResponse

from app.models.domain.user import(
    User
)

from app.models.schemas.user import(
    UserAdd,
    UserDetail
)


from app.core.database import get_db
from app.core.uau import(
    uau,
    teste
)


router = APIRouter()


@router.post(
    '/add',
    status_code=status.HTTP_200_OK,
    response_model=UserDetail
)
def add_user(data: UserAdd, response: Response, db: Session = Depends(get_db)):
    return User.add(session=db, data=data)
