from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
import app.database as db


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user = await db.get_user(event.from_user.id)
        if user is None:
            await db.add_user(tg_id=event.from_user.id, name=event.from_user.first_name)
            user = await db.get_user(event.from_user.id)
        chat = await db.get_chat(event.chat.id)
        if chat is None:
            await db.add_chat(tg_id=event.chat.id)
            chat = await db.get_chat(event.chat.id)
        user_chat_assotiation = await db.get_user_chat_association(user_id=user['id'], chat_id=chat['id'])
        if user_chat_assotiation is None:
            await db.add_user_chat_association(user_id=user['id'], chat_id=chat['id'])
            #user_chat_assotiation = await db.get_user_chat_association(user_id=user['id'], chat_id=chat['id'])
        return await handler(event, data)
