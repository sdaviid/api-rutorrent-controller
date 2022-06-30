from datetime import datetime, timedelta
from typing import(
    Union,
    List
)

from fastapi import(
    Depends,
    HTTPException,
    status
)
from fastapi.security import(
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from jose import(
    JWTError,
    jwt
)
from pydantic import BaseModel

from app.config import(
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options=options)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired JWT Token",
            headers={"WWW-Authenticate": "invalid_token"},
        )
    except JWTError as err:
        raise credentials_exception
    audience = payload.get('aud')
    if not audience == 'cli-web-torrent':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect JWT Audience",
            headers={"WWW-Authenticate": "invalid_token"},
        )
    return payload


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




class RoleValidate:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_active_user)):
        if user:
            has_break = False
            for role in user['role']:
                if role in self.allowed_roles:
                    continue
                else:
                    has_break = True
            if has_break == True:
                raise HTTPException(status_code=403, detail="Operation not permitted")




allow_create_resource = RoleValidate(["admin", "server"])
allow_access_resource = RoleValidate(["admin", "server"])



