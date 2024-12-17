import os

from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dotenv import load_dotenv


load_dotenv()
ADMINS: list = os.getenv("ADMINS")



class IsOwnerFilter(BaseFilter):
    def __init__(self, is_owner):
        self.is_owner = is_owner

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMINS

