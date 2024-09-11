import asyncio
from itertools import cycle

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.sql.functions import count, func

from bot.button import *
from db.moduls import User, session

admin_router = Router()


class AdminState(StatesGroup):
    photo = State()
    title = State()
    end=State()

@admin_router.message(F.text == "Obunachilar soni 📊", F.from_user.id == 7526654310)
async def admin(message: Message):
    query = select(count(User.id))
    counts = session.execute(query).scalars().first()
    print(counts)
    await message.answer(text=f"Obunachilar soni 📊 {counts}")


@admin_router.message(F.text == "Obunachilar ma'lumoti 📄", F.from_user.id == 7526654310)
async def admin(message: Message):
    query_count = select(count(User.id))
    counts = session.execute(query_count).scalars().first()
    for i in range(1, counts + 1):
        query = select(User).where(User.id == i)
        await message.answer(f"{session.execute(query).scalars().first()}")


@admin_router.message(F.text == "🔙 Back", F.from_user.id == 7526654310, AdminState.title)
@admin_router.message(F.text == "Reklama 🔊", F.from_user.id == 7526654310)
async def admin(message: Message, state: FSMContext):
    await message.answer("Reklama rasmini kiriting !", reply_markup=back_button())
    await state.set_state(AdminState.photo)


@admin_router.message(AdminState.photo, F.from_user.id == 7526654310, ~F.text, F.photo)
async def admin(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data({"photo": photo})
    await state.set_state(AdminState.title)
    await message.answer("Reklama haqida to'liq malumot bering !", reply_markup=back_button())


@admin_router.message(AdminState.title, F.from_user.id == 7526654310,~F.photo)
async def admin(message: Message, state: FSMContext):
    title = message.text
    await state.update_data({"title": title})
    tasks = []
    data = await state.get_data()
    await state.clear()
    counts = 0
    users = []
    cnt=0
    query_min = select(func.min(User.id))
    query_max = select(func.max(User.id))

    min_id = session.execute(query_min).scalars().first()
    max_id = session.execute(query_max).scalars().first()
    for i in range(min_id, max_id+1):

        query_user = select(User.user_id).where(User.id == i)
        user = session.execute(query_user).scalars().first()

        users.append(user)
        cnt+=1

    for i in cycle(users):
        a = message
        if counts == cnt:
            break
        if len(tasks) == 28:
            await asyncio.gather(*tasks)
            tasks = []
            try:
                 a = await message.bot.send_photo(chat_id=i, photo=data['photo'], caption=data['title'])
            except:
                pass
        tasks.append(a)
        counts += 1
    await message.answer("Reklama yuborildi !",reply_markup=admin_button())
    await state.set_state(AdminState.end)
