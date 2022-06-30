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
from app.api.deps import(
    allow_create_resource
)

router = APIRouter()



@router.post(
    '/add',
    status_code=status.HTTP_200_OK,
    response_model=ServerDetail,
    dependencies=[Depends(allow_create_resource)]
)
def add_user(
    data: ServerAdd,
    response: Response,
    db: Session = Depends(get_db)
):
    return Server.add(session=db, data=data)


@router.get(
    '/list',
    status_code=status.HTTP_200_OK,
    response_model=List[ServerDetail],
    dependencies=[Depends(allow_create_resource)]
)
def list_all(
    response: Response,
    db: Session=Depends(get_db),
):
    return Server.list_all(session=db)