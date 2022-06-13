from typing import List
from sqlalchemy.orm import Session
from fastapi import(
    Depends,
    Response,
    status,
    APIRouter
)

from fastapi.responses import JSONResponse

from app.models.domain.server import(
    Server
)

from app.models.schemas.server import(
    ServerAdd,
    ServerDetail
)


from app.core.database import get_db


router = APIRouter()



@router.post(
    '/add',
    status_code=status.HTTP_200_OK,
    response_model=ServerDetail
)
def add_user(data: ServerAdd, response: Response, db: Session = Depends(get_db)):
    return Server.add(session=db, data=data)


@router.get(
    '/list',
    status_code=status.HTTP_200_OK,
    response_model=List[ServerDetail]
)
def list_all(response: Response, db: Session=Depends(get_db)):
    return Server.list_all(session=db)