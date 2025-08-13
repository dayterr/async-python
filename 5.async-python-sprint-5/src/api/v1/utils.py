import os
from datetime import datetime, timedelta
from typing import Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from src.schemas.entity import TokenPayload, TokenSchema

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl='/login',
    scheme_name='JWT',
    auto_error=False,
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = 'HS256'
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY', '')

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {'expires': str(expires_delta), 'subject': str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {'expires': str(expires_delta), 'subject': str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str | None = Depends(reuseable_oauth)):
    datetime_str = '%Y-%m-%d %H:%M:%S.%f'
    if token is None:
        return
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if datetime.strptime(token_data.expires, datetime_str) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return token_data.subject


async def save_file_to_dir(file_content, filename: str):
    directory = filename.rsplit('/', 1)[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f'{filename}', "wb") as uploaded_file:
        uploaded_file.write(file_content)
        uploaded_file.close()


def get_file_size(filename: str):
    return os.path.getsize(filename)
