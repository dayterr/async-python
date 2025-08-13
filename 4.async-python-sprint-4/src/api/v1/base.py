from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from schemas import entity
from services.entity import entity_crud, entity_user_crud

from .utils import (create_access_token,
                    create_refresh_token,
                    get_current_user,
                    get_hashed_password,
                    verify_password)

router = APIRouter()


@router.post('/urls', status_code=status.HTTP_201_CREATED)
async def add_url(request: Request,
                  url: entity.ShortenedUrlBase,
                  db: AsyncSession = Depends(get_session),
                  login: str = Depends(get_current_user)):
    short_url = str(uuid4())
    url_model = entity.ShortenedUrlCreate(full_url=url.full_url, short_url=short_url, clicks=0, type=url.type)
    if login is not None:
        usr = await entity_user_crud.get(db=db, login=login)
        if usr is not None:
            url_model.user = usr.id
    url_created = await entity_crud.create(db=db, obj_in=url_model)
    return url_created


@router.get('/urls/{url_id}')
async def get_url(url_id: int,
                  db: AsyncSession = Depends(get_session)):
    url_item = await entity_crud.get(db=db, id=url_id)
    response = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.headers['Location'] = url_item.full_url
    if not url_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Item not found'
        )
    if url_item.is_deleted:
        return Response(status_code=status.HTTP_410_GONE)
    return response


@router.get('/urls/{url_id}/status')
async def get_url_status(url_id: int,
                         db: AsyncSession = Depends(get_session)):
    url_item = await entity_crud.get(db=db, id=url_id)
    jsn = jsonable_encoder({'clicks': url_item.clicks})
    rsp = ORJSONResponse(content=jsn)
    return rsp


@router.delete('/urls/{url_id}')
async def delete_url(url_id: int,
                     db: AsyncSession = Depends(get_session)):
    entity = await entity_crud.delete(db=db, url_id=url_id)
    return status.HTTP_200_OK


@router.post('/users/signup')
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


@router.post('/users/login')
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


@router.get('/user/status')
async def get_user_urls(db: AsyncSession = Depends(get_session),
                        login: str = Depends(get_current_user)):
    usr = await entity_user_crud.get(db=db, login=login)
    if usr is None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect data'
            )
    urls = await entity_crud.get_many(db=db, user_id=usr.id)
    jsn = jsonable_encoder(urls)
    rsp = ORJSONResponse(content=jsn)
    return rsp


@router.patch('/urls/{url_id}')
async def patch_user_url(url_id: int,
                         request: Request,
                         url: entity.ShortenedUrlUpdate,
                         db: AsyncSession = Depends(get_session),
                         login: str = Depends(get_current_user)):
    usr = await entity_user_crud.get(db=db, login=login)
    if usr is None:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authorized'
            )
    url_item = await entity_crud.get(db=db, id=url_id)
    if url_item.user != usr.id:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='This url was created by a different user'
            )
    entity = await entity_crud.update_type(db=db, url_id=url_id, tpe=url.type)
    return status.HTTP_200_OK


@router.get('/{short_url}')
async def get_short_url(short_url: str,
                        db: AsyncSession = Depends(get_session)):
    entity = await entity_crud.update(db=db, short_url=short_url)
    return status.HTTP_200_OK
