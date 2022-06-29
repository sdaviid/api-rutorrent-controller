from datetime import datetime, timedelta
from typing import Union

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
from app.models.schemas.token import(
    Token,
    TokenData
)

from app.core.database import SessionLocal



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
        token_data = TokenData(username=username)
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
        raise credentials_exception
    return payload.get('sub')


async def get_current_active_user(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user