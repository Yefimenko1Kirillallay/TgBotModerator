from datetime import datetime, timedelta
from .model import async_session
from .model import User, Chat, User_chat_association, UserMessage, Topic, User_say, Bot_answer
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func

from config import *


async def get_user(tg_id) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user is None:
                return None
            user = user.__dict__
            user = {'id': user['id'], 'tg_id': user['tg_id'], 'name': user['name']}
            return user


async def get_user_by_id(user_id) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.id == user_id))
            if user is None:
                return None
            user = user.__dict__
            user = {'id': user['id'], 'tg_id': user['tg_id'], 'name': user['name']}
            return user


async def add_user(tg_id, name) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()


async def get_chat(tg_id) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            chat = await session.scalar(select(Chat).where(Chat.tg_id == tg_id))
            if chat is None:
                return None
            chat = chat.__dict__
            chat = {'id': chat['id'], 'tg_id': chat['tg_id']}
            return chat


async def get_chat_by_id(chat_id) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            chat = await session.scalar(select(Chat).where(User.id == chat_id))
            if chat is None:
                return None
            chat = chat.__dict__
            chat = {'id': chat['id'], 'tg_id': chat['tg_id']}
            return chat


async def add_chat(tg_id) ->  None:
    async with async_session() as session:
        async with session.begin():
            session.add(Chat(tg_id=tg_id))
            await session.commit()


async def get_user_chat_association(as_id=None, user_id=None, chat_id=None) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            if as_id:
                association = await session.scalar(select(User_chat_association)
                                                   .where(User_chat_association.id == as_id))
            elif user_id and chat_id:
                association = await session.scalar(select(User_chat_association).
                                                   where(User_chat_association.user_id == user_id,
                                                         User_chat_association.chat_id == chat_id))
            else:
                return None
            if association is None:
                return None
            else:
                association = association.__dict__
                association = {'id': association['id'], 'user_id': association['user_id'],
                               'chat_id': association['chat_id'], 'mat': association['mat'],
                               'links': association['links']}
                return association


async def add_user_chat_association(user_id, chat_id) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(User_chat_association(user_id=user_id, chat_id=chat_id))
            await session.commit()


async def add_waring(user_id, chat_id, waring, type) -> None:
    async with async_session() as session:
        async with session.begin():
            if type == 'mat':
                await session.execute(update(User_chat_association)
                                      .where(User_chat_association.user_id == user_id,
                                             User_chat_association.chat_id == chat_id)
                                      .values(mat=waring))
            elif type == 'links':
                await session.execute(update(User_chat_association)
                                      .where(User_chat_association.user_id == user_id,
                                             User_chat_association.chat_id == chat_id)
                                      .values(links=waring))
            await session.commit()


async def flood_time_mes(user_id, chat_id) -> int:
    async with async_session() as session:
        async with session.begin():
            now = datetime.now()

            # Добавляем запись о новом сообщении в базу данных
            session.add(UserMessage(user_id=user_id, chat_id=chat_id, timestamp=now))

            # Удаляем старые записи (вышедшие за пределы временного окна)
            await session.execute(
                UserMessage.__table__.delete().where(
                    UserMessage.chat_id == chat_id,
                    UserMessage.user_id == user_id,
                    UserMessage.timestamp < now - animation_time_limit))

            # Подсчитываем количество сообщений пользователя за временное окно
            result = await session.execute(
                select(func.count(UserMessage.id)).where(
                    UserMessage.chat_id == chat_id,
                    UserMessage.user_id == user_id,
                    UserMessage.timestamp >= now - animation_time_limit
                )
            )
            flood_count = result.scalar_one_or_none()
            await session.commit()
            return flood_count


#-------------------------------------------------------------------------------------------------------------------
async def add_topic(text) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(Topic(text=text))
            await session.commit()


async def get_topics() -> list | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.scalars(select(Topic))
            if result is None:
                return None
            topics = [topic.__dict__ for topic in result]
            topic_list = []
            for topic in topics:
                topic_list.append({'id': topic['id'], 'text': topic['text']})
            return topic_list


async def get_topic_by_id(topic_id) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            topic = await session.scalar(select(Topic).where(Topic.id == topic_id))
            if topic is None:
                return None
            topic = topic.__dict__
            topic = {'id': topic['id'], 'text': topic['text']}
            return topic


async def get_topic_by_text(text) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            topic = await session.scalar(select(Topic).where(Topic.text == text))
            if topic is None:
                return None
            topic = topic.__dict__
            topic = {'id': topic['id'], 'text': topic['text']}
            return topic


async def add_UserSay(text, topic_id) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(User_say(text=text, topic_id=topic_id))
            await session.commit()


async def get_UserSay_by_text(text):
    async with async_session() as session:
        async with session.begin():
            say = await session.scalar(select(User_say).where(User_say.text == text))
            if say is None:
                return None
            say = say.__dict__
            say = {'id': say['id'], 'text': say['text'], 'topic_id': say['topic_id']}
            return say


async def get_UserSay_by_topic_id(topic_id) -> list | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.scalars(select(User_say).where(User_say.topic_id == topic_id))
            if result is None:
                return None
            says = [say.__dict__ for say in result]
            say_list = []
            for say in says:
                say_list.append({'id': say['id'], 'text': say['text'], 'topic_id': say['topic_id']})
            return say_list


async def add_BotAnswer(text, topic_id) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add(Bot_answer(text=text, topic_id=topic_id))
            await session.commit()


async def get_BotAnswer_by_text(text) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            answer = await session.scalar(select(Bot_answer).where(Bot_answer.text == text))
            if answer is None:
                return None
            answer = answer.__dict__
            answer = {'id': answer['id'], 'text': answer['text'], 'topic_id': answer['topic_id']}
            return answer


async def get_BotAnswer_by_topic_id(topic_id) -> list | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.scalars(select(Bot_answer).where(Bot_answer.topic_id == topic_id))
            if result is None:
                return None
            answers = [answer.__dict__ for answer in result]
            answer_list = []
            for answer in answers:
                answer_list.append({'id': answer['id'], 'text': answer['text'], 'topic_id': answer['topic_id']})
            return answer_list
