import asyncio
from datetime import datetime, timedelta
import logging
import xml.etree.ElementTree as ET

import aiohttp
from aiohttp import ClientError

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from setup import get_db, engine
import models
import schemas


logging.basicConfig(format="%(levelname)s:     %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


models.Base.metadata.create_all(engine)


async def get_news() -> None:
    """ Скачивание новостей с источников """
    
    logger.info("Running get news from source.")
    for db in get_db():
        sources = db.query(models.Source).all()
        async with aiohttp.ClientSession() as session:
            for source in sources:
                try:
                    async with session.get(source.url) as response:
                        root = ET.fromstring(await response.text())
                        channel = root.find('channel')
                        for item in channel.findall('item'):
                            title = item.find("title").text
                            description = item.find("description").text if item.find("description").text else "Описание отсутсвует"
                            pub_date = item.find("pubDate").text

                            existing_news = db.query(models.News).filter(
                                models.News.title == title,
                            ).first()
                            if not existing_news:
                                news = models.News(
                                    title=title,
                                    description=description,
                                    pub_date=pub_date,
                                    source_id=source.id
                                )
                                db.add(news)
                except ClientError as e:
                    logger.error(f"Not to get news from {source.url}: {e}")
        db.commit()


async def run_get_news():
    while True:
        await get_news()
        await asyncio.sleep(600)


app = FastAPI(
    on_startup=[lambda: asyncio.create_task(run_get_news())],
)


@app.get("/api/v1", response_class=JSONResponse)
async def root() -> JSONResponse:
    """ Корневой путь """

    return JSONResponse(content={"message": "News API"}, status_code=200)


@app.post("/api/v1/user", response_class=JSONResponse)
async def user(
    user: schemas.User,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """Получить данные пользователя, проверить, есть ли они в базе данных, и вернуть ответ"""

    existing_user = db.query(models.User).filter(
        models.User.id == user.id).first()

    if existing_user:
        return JSONResponse(content={"message": f"С возвращением {user.username}!!!"}, status_code=200)
    else:
        new_user = models.User(
            id=user.id, username=user.username, full_name=user.full_name)
        db.add(new_user)
        db.commit()
        return JSONResponse(content={"message": f"Добро пожаловать {user.username}!!!"}, status_code=201)


@app.post("/api/v1/add", response_class=JSONResponse)
async def add_source(
    user: schemas.UserBase,
    url: schemas.Url,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """ Добавление источника от пользователя """
    url_str = str(url.url)
    
    existing_user = db.query(models.User).get(user.id)
    if existing_user:
        return JSONResponse(content={"message": "Пользователь не найден"}, status_code=404)

    existing_source = db.query(models.Source).filter(
        models.Source.url == url_str).first()
    if existing_source:
        existing_source_from_user = db.query(models.UsersSource).\
            filter(models.UsersSource.user_id == existing_user.id, models.UsersSource.source_id == existing_source.id).\
            first()
        if existing_source_from_user is None:
            existing_user.sources.append(existing_source)
        else:
            return JSONResponse(content={"message": "Источник уже добавлен"}, status_code=403)
    else:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url_str) as response:
                    root = ET.fromstring(await response.text())
                    channel = root.find('channel')

                    new_source = models.Source(
                        title=channel.find('title').text,
                        description=channel.find('description').text,
                        url=url_str
                    )
                    db.add(new_source)
                    existing_user.sources.append(new_source)
            except ClientError:
                return JSONResponse(content={"message": "Источник недоступен"}, status_code=404)
    db.commit()

    return JSONResponse(content={"message": "Источник успешно добавлен"}, status_code=200)


@app.post("/api/v1/news/hour", response_model=list[schemas.News])
async def news_hour(
    user: schemas.UserBase, 
    db: Session = Depends(get_db)
) -> JSONResponse:
    """ Получить новости за последний час """

    existing_user = db.query(models.User).get(user.id)
    if existing_user:
        return JSONResponse(content={"message": "Пользователь не найден"}, status_code=404)

    hour_ago = datetime.now() - timedelta(hours=1)
    news = db.query(models.News).\
        join(models.Source).\
        filter(models.News.pub_date > hour_ago, models.Source.users.any(models.User.id == user.id)).\
        all()

    return news


@app.post("/api/v1/news/day", response_model=list[schemas.News])
async def news_day(
    user: schemas.UserBase, 
    db: Session = Depends(get_db)
) -> JSONResponse:
    """ Получить новости за последние сутки """

    existing_user = db.query(models.User).get(user.id)
    if existing_user:
        return JSONResponse(content={"message": "Пользователь не найден"}, status_code=404)

    day_ago = datetime.now() - timedelta(days=1)
    news = db.query(models.News).\
        join(models.Source).\
        filter(models.News.pub_date > day_ago, models.Source.users.any(models.User.id == user.id)).\
        all()

    return news
