from pydantic import BaseModel


class ShortenedUrlBase(BaseModel):
    """Shared properties"""
    full_url: str
    short_url: str | None = None
    clicks: int | None = 0
    type: str | None = 'public'
    is_deleted: bool | None = False
    user: int | None = None


class ShortenedUrlCreate(ShortenedUrlBase):
    """Properties to receive on entity creation"""
    pass


class ShortenedUrlUpdate(BaseModel):
    """Properties to receive on entity update"""
    type: str


class ShortenedUrlInDBBase(ShortenedUrlBase):
    """Properties shared by models stored in DB"""
    full_url: str
    short_url: str
    clicks: int
    type: str
    is_deleted: bool
    user: int

    class Config:
        orm_mode = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    expires: str
    subject: str


class ShortenedUrl(ShortenedUrlInDBBase):
    """Properties to return to client"""
    pass


class ShortenedUrlInDB(ShortenedUrlInDBBase):
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
