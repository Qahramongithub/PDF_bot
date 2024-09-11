from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def pdf_button():
    ikb = InlineKeyboardBuilder()
    ikb.add(*[
        InlineKeyboardButton(text="Davom etish ", callback_data="pdf"),
        InlineKeyboardButton(text="Pdf tayorlash", callback_data="tayor")
    ])
    return ikb.as_markup()

def admin_button():
    rkb = ReplyKeyboardBuilder()
    rkb.add(
        *[
            KeyboardButton(text="Reklama 🔊"),
            KeyboardButton(text="Obunachilar soni 📊"),
            KeyboardButton(text="Obunachilar ma'lumoti 📄"),
            KeyboardButton(text="Admin qushish 🎟")
        ]
    )
    rkb.adjust(2, 1)
    return rkb.as_markup(resize_keyboard=True)


def back_button():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="🔙 Back"),
    ])
    rkb.adjust(1)
    return rkb.as_markup(resize_keyboard=True)
