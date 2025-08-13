from pydantic import BaseModel


class FileBase(BaseModel):
    """Shared properties"""
    name: str
    path: str
    is_downloadable: bool | None = True
    user: int
    size: int


class FileCreate(FileBase):
    """Properties to receive on entity creation"""
    pass


class FileUpdate(BaseModel):
    """Properties to receive on entity update"""
    type: str


class FileInDBBase(FileBase):
    """Properties shared by models stored in DB"""
    name: str
    is_downloadable: bool | None = True
    user: int

    class Config:
        orm_mode = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    expires: str
    subject: str


class File(FileInDBBase):
    """Properties to return to client"""
    pass


class FileInDB(FileInDBBase):
    """Properties stored in DB"""
    pass


class UserBase(BaseModel):
    login: str
    password: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    login: str
    password: str

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    pass
