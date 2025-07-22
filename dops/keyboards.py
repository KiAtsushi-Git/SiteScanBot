from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

async def answer_kb():
    kb = InlineKeyboardMarkup()

    scan_ports_but = InlineKeyboardButton(text="Сканирование популярных портов", callback_data="scan_popular_ports")
    do_graph_but = InlineKeyboardButton(text="Создать граф связи", callback_data="do_graph")

    kb.row(scan_ports_but)
    kb.row(do_graph_but)
    return kb