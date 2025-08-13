from models.entity import ShortenedUrl, User
from schemas.entity import (ShortenedUrlCreate,
                            ShortenedUrlUpdate,
                            UserCreate,
                            UserUpdate)

from .base import RepositoryDB, UserDB


class RepositoryEntity(RepositoryDB[ShortenedUrl,
                                    ShortenedUrlCreate, ShortenedUrlUpdate]):
    pass


class UserEntity(UserDB[User, UserCreate, UserUpdate]):
    pass


entity_crud = RepositoryEntity(ShortenedUrl)
entity_user_crud = UserEntity(User)
