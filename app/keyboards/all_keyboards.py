from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from config import *


async def confirm_rules_keyboard(user_id):
    confirm_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Правила", url=rules_url)],
        [InlineKeyboardButton(text="Прочитал правила", callback_data=f"confirm_rules_{user_id}")]])
    return confirm_button
