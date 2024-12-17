from sqlalchemy import ForeignKey, String, BigInteger, Boolean, Integer, Date, Time, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import os
import logging
import asyncio
import datetime
from datetime import date, time
import aiosqlite
import greenlet

from dotenv import load_dotenv

# Включаем логирование
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

load_dotenv()

DB_URL = os.getenv('DB_URL')

engine = create_async_engine(url=DB_URL, echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(20))

    associations = relationship('User_chat_association', back_populates='user')


class Chat(Base):
    __tablename__ = 'chats'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)

    associations = relationship('User_chat_association', back_populates='chat')


class User_chat_association(Base):
    __tablename__ = 'user_chat_associations'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    mat: Mapped[int] = mapped_column(default=0)
    links: Mapped[int] = mapped_column(default=0)

    chat = relationship('Chat', back_populates='associations')
    user = relationship('User', back_populates='associations')


class UserMessage(Base):
    __tablename__ = "user_messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(nullable=False)

    user_say = relationship('User_say', back_populates='say_user')
    bot_answ = relationship('Bot_answer', back_populates='bot_answ')


class User_say(Base):
    __tablename__ = "user_says"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'), nullable=False)

    say_user = relationship('Topic', back_populates='user_say')


class Bot_answer(Base):
    __tablename__ = "bot_answers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'), nullable=False)

    bot_answ = relationship('Topic', back_populates='bot_answ')


async def db_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
