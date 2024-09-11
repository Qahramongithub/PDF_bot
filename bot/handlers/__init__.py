from aiogram import Dispatcher

from bot.handlers.admin import admin_router
from bot.handlers.start import start_router

dp = Dispatcher()

dp.include_routers(
    *[
        start_router, admin_router
    ]
)
