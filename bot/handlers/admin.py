import asyncio
from itertools import cycle

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from bot.button import *
from db.moduls import User, session

admin_router = Router()


class AdminState(StatesGroup):
    photo = State()
    title = State()


@admin_router.message(F.text == "Obunachilar soni 📊", F.from_user.id == 7033073770)
async def admin(message: Message):
    query = select(count(User.id))
    counts = session.execute(query).scalars().first()
    print(counts)
    await message.answer(text=f"Obunachilar soni 📊 {counts}")


@admin_router.message(F.text == "Obunachilar ma'lumoti 📄", F.from_user.id == 7033073770)
async def admin(message: Message):
    query_count = select(count(User.id))
    counts = session.execute(query_count).scalars().first()
    for i in range(1, counts + 1):
        query = select(User).where(User.id == i)
        await message.answer(f"{session.execute(query).scalars().first()}")


@admin_router.message(F.text == "🔙 Back", F.from_user.id == 7033073770, AdminState.title)
@admin_router.message(F.text == "Reklama 🔊", F.from_user.id == 7033073770)
async def admin(message: Message, state: FSMContext):
    await message.answer("Reklama rasmini kiriting !", reply_markup=back_button())
    await state.set_state(AdminState.photo)


@admin_router.message(AdminState.photo, F.from_user.id == 7033073770, ~F.text, F.photo)
async def admin(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data({"photo": photo})
    await state.set_state(AdminState.title)
    await message.answer("Reklama haqida to'liq malumot bering !", reply_markup=back_button())


@admin_router.message(AdminState.title, F.from_user.id == 7033073770, ~F.photo)
async def admin(message: Message, state: FSMContext):
    title = message.text
    await state.update_data({"title": title})
    tasks = []
    data = await state.get_data()
    await state.clear()
    counts = 0
    users = []
    query_count = select(count(User.id))
    cnt = session.execute(query_count).scalars().first()
    for i in range(1, cnt + 1):
        query_user = select(User.user_id).where(User.id == i)
        user = session.execute(query_user).scalars().first()
        users.append(user)
    for i in cycle(users):
        if counts == cnt:
            break
        if len(tasks) == 28:
            await asyncio.gather(*tasks)
            tasks = []
        tasks.append(await message.bot.send_photo(chat_id=i, photo=data['photo'], caption=data["title"]))
        counts += 1
