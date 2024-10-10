from sqlalchemy import ForeignKey, UniqueConstraint, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class UsersSource(Base):
    """ Таблица для связи многие ко многим  между таблицами users и sources """


    __tablename__ = 'users_source'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    source_id = Column(Integer, ForeignKey('sources.id'))


class User(Base):
    """ Таблица для хранения данных о пользователях """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    sources = relationship(
        "Source", secondary=UsersSource.__tablename__, back_populates="users")


class News(Base):
    """ Таблица для хранения новостей """

    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    pub_date = Column(DateTime, nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'))

    source = relationship("Source", back_populates="news")

    __table_args__ = (UniqueConstraint('title', name='UK_NEWS_TITLE'),)


class Source(Base):
    """ Таблица для хранения данных исчтоников новостей """

    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    url = Column(String, nullable=False)

    news = relationship("News", back_populates="source")
    users = relationship(
        "User", secondary=UsersSource.__tablename__, back_populates="sources")

    __table_args__ = (UniqueConstraint('url', name='UK_SOURCE_URL'),)
