from datetime import datetime
from pydantic import BaseModel, HttpUrl


class UserBase(BaseModel):
    """ Базовая модель для пользователей """
    id: int


class User(UserBase):
    """ Схема для пользователей """

    username: str
    full_name: str


class Source(BaseModel):
    """ Схема для источников """
    title: str
    description: str
    url: str


class News(BaseModel):
    """ Схема для новостей """
    title: str
    description: str
    pub_date: datetime
    source: Source

    class Config:
        from_attributes=True


class Url(BaseModel):
    """ Схема для ссылок """

    url: HttpUrl
