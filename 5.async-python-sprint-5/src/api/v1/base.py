from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, Response
from starlette.responses import FileResponse
from sqlalchemy.exc import InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.schemas import entity
from src.services.entity import entity_crud, entity_user_crud

from .utils import (create_access_token,
                    create_refresh_token,
                    get_current_user,
                    get_hashed_password,
                    get_file_size,
                    save_file_to_dir,
                    verify_password)

router = APIRouter()


@router.post('/register',
             summary='Регистрация пользователя',
             description='Регистрация пользователя с помощью логина и пароля',
)
async def create_user(request: Request,
                      db: AsyncSession = Depends(get_session)):
    data = await request.json()
    login = data.get('login')
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data format'
        )
    user_item = await entity_user_crud.get(db=db, login=login)
    if user_item is not None:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail='User already registered'
            )
    password = data.get('password')
    if password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data format'
        )
    hashed_password = get_hashed_password(password)
    user_model = entity.UserCreate(login=login, password=hashed_password)
    user_item = await entity_user_crud.create(db=db, obj_in=user_model)
    return user_item


@router.post('/auth',
             summary='Аутентификация пользователя',
             description='Аутентификация пользователя с помощью логина и пароля для получения токена',
)
async def login(request: Request,
                db: AsyncSession = Depends(get_session)):
    data = await request.json()
    login = data.get('login')
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data format'
        )
    user_item = await entity_user_crud.get(db=db, login=login)
    password = data.get('password')
    if password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data format'
        )
    hashed_pass = user_item.password
    if not verify_password(password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect password'
        )
    return {
        'access_token': create_access_token(login),
        'refresh_token': create_refresh_token(login),
    }


@router.post('/files/upload',
             summary='Загрузка файла',
             description='Загрузка файла, доступна только авторизованному пользователю',
)
async def upload_file(name: Optional[str],
                      file: UploadFile = File(...),
                      db: AsyncSession = Depends(get_session),
                      login: str = Depends(get_current_user)):

    filename = name.rsplit('/', 1)[-1]
    file_content = await file.read()
    await save_file_to_dir(file_content, name)
    size = get_file_size(name)
    usr = await entity_user_crud.get(db=db, login=login)
    if usr is None:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authorized'
            )
    file_model = entity.FileCreate(name=filename, path=name, size=size, user=usr.id)

    file_created = await entity_crud.create(db=db, obj_in=file_model)
    return file_created


@router.get('/files/download',
            summary='Скачивание файла',
            description='Скачивание файла, доступно только авторизованному пользователю',
)
async def download_file(path: str,
                        db: AsyncSession = Depends(get_session),
                        login: str = Depends(get_current_user)):
    usr = await entity_user_crud.get(db=db, login=login)
    if usr is None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data'
            )
    file_info_from_db = await entity_crud.get(db=db, path=path)
    if file_info_from_db:
        file_resp = FileResponse(file_info_from_db.path)
        response = Response(status_code=status.HTTP_200_OK)
        return file_resp
    else:
        response = Response(status_code=status.HTTP_404_NOT_FOUND)
        return response


@router.get('/files/list',
            summary='Файлы пользователя',
            description='Список файлов, загруженных пользователем',
)
async def list_user_files(db: AsyncSession = Depends(get_session),
                          login: str = Depends(get_current_user)):
    usr = await entity_user_crud.get(db=db, login=login)
    if usr is None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data'
            )
    files = await entity_crud.get_many(db=db, user_id=usr.id)
    jsn = jsonable_encoder(files)
    rsp = ORJSONResponse(content=jsn)
    return rsp


@router.post('/files/search',
             summary='Поиск файла',
             description='Поиск файла по заданным параметрам',
)
async def search_files(name: Optional[str] = None,
                       path: Optional[str] = None,
                       size: Optional[int] = None,
                       db: AsyncSession = Depends(get_session),
                       login: str = Depends(get_current_user)):
    usr = await entity_user_crud.get(db=db, login=login)
    if usr is None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data'
            )
    files = await entity_crud.get_by_params(db=db, name=name, path=path, size=size)
    jsn = jsonable_encoder(files)
    rsp = ORJSONResponse(content=jsn)
    return rsp


@router.get('/ping',
            summary='Проверка базы данных',
            description='Проверка статуса базы данных',
)
async def ping_db(db: AsyncSession = Depends(get_session),
                  login: str = Depends(get_current_user)):
    try:
        usr = await entity_user_crud.get(db=db, login=login)
        if usr is None:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data'
                )
        return usr
    except InterfaceError:
        raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Something wrong with DB'
                )
