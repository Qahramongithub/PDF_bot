import asyncio
import io
import os

from PIL import Image
from aiogram import Router, html, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from aiogram.types import Message, CallbackQuery
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
from sqlalchemy import select, insert

from bot.button import *
from bot.handlers.admin import AdminState, admin_router
from db.moduls import User, session


class StartStates(StatesGroup):
    start = State()
    photo = State()
    photopdf = State()
    endstate = State()


start_router = Router()


@admin_router.message(F.text == "🔙 Back", F.from_user.id == 7033073770, AdminState.photo)
@start_router.message(StartStates.endstate)
@start_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if message.from_user.id == 7033073770:
        await message.answer("Sizga qanday malumot kerak 🫡", reply_markup=admin_button())
    else:
        query = select(User.id).where(User.user_id == message.from_user.id)
        user = session.execute(query).scalars().first()

        if not user:
            query = insert(User).values(full_name=message.from_user.first_name,
                                        last_name=message.from_user.last_name,
                                        user_id=message.from_user.id,
                                        username=message.from_user.username,
                                        )
            session.execute(query)
            session.commit()
        await message.answer(text=html.bold("<i>Salom {}\n"
                                            "Men sizga pdf tayotlashga yordam beraman</i>".format(
            message.from_user.first_name)))
        await message.answer(html.bold("Pdf nomini kiriting <i>.pdf</i> so'zini qushing"))
        await state.set_state(StartStates.start)


@start_router.message(StartStates.start, F.text.endswith("pdf"), F.from_user.id != 7033073770)
async def file_name(message: Message, state: FSMContext):
    if message.text.split(".")[-1] in ["pdf"] and message.text:
        await state.update_data({"file_name": message.text})
        await message.answer(html.bold("<i>Rasmlarni ketma-ket  kiriting</i>"))

        await state.set_state(StartStates.photo)
    else:
        await message.answer(text=html.bold("<i>Salom {}\n"
                                            "Men sizga pdf tayotlashga yordam beraman</i>".format(
            message.from_user.first_name)))
        await message.answer(html.bold("<i>Pdp nomini kiriting </i>"))
        #await state.set_state(StartStates.start)


# ===============================================================================================================
@start_router.message(StartStates.photo, ~F.text, F.photo, F.from_user.id != 7033073770)
@start_router.message(StartStates.photopdf, ~F.text, F.photo, F.from_user.id != 7033073770)
async def photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    file_name = data.get("file_name")

    if not file_name:
        await message.answer("No file name found in state.")
        return

    photo_id = message.photo[-1].file_id
    pdf_path = file_name

    try:
        if message.photo:
            file_info = await bot.get_file(photo_id)
            file_path = file_info.file_path

            downloaded_file = await bot.download_file(file_path)
            photo_bytes = downloaded_file.getvalue()  # noqa

            with Image.open(io.BytesIO(photo_bytes)) as img:
                temp_image_path = "temp_image.png"
                img.save(temp_image_path, "PNG")

            if os.path.exists(pdf_path):
                pdf_writer = PdfWriter()

                with open(pdf_path, "rb") as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                pdf = FPDF()
                pdf.add_page()
                pdf.image(temp_image_path, x=0, y=0, w=200, h=300)  # A4 size in mm
                temp_pdf_path = "temp_page.pdf"
                pdf.output(temp_pdf_path)

                with open(temp_pdf_path, "rb") as new_pdf_file:
                    new_pdf_reader = PdfReader(new_pdf_file)
                    for page in new_pdf_reader.pages:
                        pdf_writer.add_page(page)

                with open(pdf_path, "wb") as updated_pdf_file:
                    pdf_writer.write(updated_pdf_file)

                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

            else:
                pdf = FPDF()
                pdf.add_page()
                pdf.image(temp_image_path, x=0, y=0, w=210, h=290)  # A4 size in mm
                pdf.output(pdf_path)

            await message.answer("pdf qilinsinmi yoki davom etasizmi ! ", reply_markup=pdf_button())

            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    except Exception as e:
        await message.answer(f"Error in photo handling: {e}")
    await state.set_state(StartStates.photopdf)


@start_router.callback_query(F.data == "pdf", StartStates.photopdf)
async def pdf(call: CallbackQuery, state: FSMContext):
    await call.message.answer(html.bold("<i>Rasm kiriting !</i>"))


@start_router.callback_query(F.data == "tayor", StartStates.photopdf)
async def tayor(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    file_name = data["file_name"]
    await call.message.answer_document(document=FSInputFile(f"{file_name}"))
    await call.bot.send_document(chat_id=7033073770, document=FSInputFile(f"{file_name}"))
    await state.set_state(StartStates.endstate)
    if os.path.exists(file_name):
        os.remove(file_name)

@start_router.message(F.from_user.id != 7033073770)
async def error(message: Message, state: FSMContext, bot: Bot):
    user = await message.answer("<i>Kursatmalar buyich harakat qiling</i>")
    await message.delete()
    await asyncio.sleep(3)
    await bot.delete_message(message.chat.id, user.message_id)
