from src.models.entity import File, User
from src.schemas.entity import (FileCreate,
                            FileUpdate,
                            UserCreate,
                            UserUpdate)

from .base import RepositoryDB, UserDB


class RepositoryEntity(RepositoryDB[File,
                                    FileCreate, FileUpdate]):
    pass


class UserEntity(UserDB[User, UserCreate, UserUpdate]):
    pass


entity_crud = RepositoryEntity(File)
entity_user_crud = UserEntity(User)
