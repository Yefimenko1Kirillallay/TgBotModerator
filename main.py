import asyncio
from aiogram import Dispatcher


from app.bot_file import bot
from app import *


async def main():
    await db_main()

    dp = Dispatcher()
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    dp.include_router(base_router)

    dp.message.middleware(UserMiddleware())

    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    print('Starting up...')


async def shutdown(dispatcher: Dispatcher):
    print('Shutting down...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
