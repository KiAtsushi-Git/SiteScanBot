import time
import re
from dops.config import *
from dops.keyboards import *
from utils.scan import *
from utils.reafact import *
from utils.graph import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile


bot = Bot(BotToken)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("<b>Добро пожаловать в бота сканера сайтов!\nЧтобы начать просто отправь ссылку:</b>", parse_mode="HTML")

@dp.message_handler()
async def handle_domain(msg: types.Message):
    chat_id = msg.chat.id
    url = msg.text.strip()

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    domain = extract_domain(url)
    if "." in domain:
        st_msg = await msg.answer(f"🔍 Найден домен: <code>{domain}</code>", parse_mode="HTML")
        ips = await get_ip(domain)
        if isinstance(ips, str):
            return ips

        dns = await get_dns_records(domain)

        server_info_result = {}
        for ip in ips:
            info = await get_server_info(ip)
            server_info_result[ip] = info
        data = f"🔍 Найден домен: <code>{domain}</code>\n"
        data += "<b>IP адреса:</b>\n" + "\n".join(ips) + "\n\n"
        data += "<b>DNS записи:</b>\n"
        for rtype, recs in dns.items():
            data += f"<b>{rtype}:</b> {', '.join(recs) if recs else 'нет данных'}\n\n"
        data += "<b>Информация о сервере:</b>\n"
        for ip, info in server_info_result.items():
            data += f"{ip}:\n"
            if "error" in info:
                data += f"  Ошибка: {info['error']}\n"
            else:
                for k, v in info.items():
                    data += f"  {k}: {v}\n"
            data += "\n"

        await bot.edit_message_text(message_id=st_msg.message_id, chat_id=chat_id, text="[==========]", parse_mode="HTML")
        time.sleep(0.1)
        await bot.edit_message_text(message_id=st_msg.message_id, chat_id=chat_id, text="[###=======]", parse_mode="HTML")
        time.sleep(0.1)
        await bot.edit_message_text(message_id=st_msg.message_id, chat_id=chat_id, text="[#######===]", parse_mode="HTML")
        time.sleep(0.1)
        await bot.edit_message_text(message_id=st_msg.message_id, chat_id=chat_id, text="[##########]",parse_mode="HTML")
        time.sleep(0.1)
        await bot.edit_message_text(message_id=st_msg.message_id, chat_id=chat_id, text=data, parse_mode="HTML", reply_markup=await answer_kb())
    else:
        await msg.answer("⚠️ Не удалось распознать ссылку или домен. Попробуй ещё раз.")


@dp.callback_query_handler(lambda c: c.data.startswith("scan_popular_ports"))
async def callback_info(call: types.CallbackQuery):
    message_text = call.message.text

    ip_block_match = re.search(r"IP адреса:\s*([\s\S]+?)\n\n", message_text)
    if ip_block_match:
        ip_block = ip_block_match.group(1)
        ip_list = re.findall(r"[0-9a-fA-F:.]{4,}", ip_block)
    else:
        ip_list = []

    open_ports_result = {}
    for ip in ip_list:
        open_ports = await scan_ports(ip)
        open_ports_result[ip] = open_ports

    text = "🧩 IP-адреса из блока:\n"
    text += "\n".join(f"• <code>{ip}</code>" for ip in ip_list)

    text += "\n\n🔎 Открытые порты:\n"
    for ip, ports in open_ports_result.items():
        if ports:
            ports_str = ", ".join(str(p) for p in ports)
            text += f"<b>{ip}</b>: {ports_str}\n"
        else:
            text += f"<b>{ip}</b>: нет открытых популярных портов\n"

    await call.answer()
    await call.message.answer(text, parse_mode="HTML")



@dp.callback_query_handler(lambda c: c.data.startswith("do_graph"))
async def callback_info(call: types.CallbackQuery):
    message_text = call.message.text

    import re
    domain_match = re.search(r"домен:\s*(\S+)", message_text, re.IGNORECASE)
    domain = domain_match.group(1) if domain_match else None

    if not domain:
        await call.answer("Не удалось получить домен из сообщения", show_alert=True)
        return

    await call.answer("Начинаю сканирование и построение графа...")

    # Получаем данные
    ips, open_ports, server_info, dns = await scan_domain_data(domain)
    if ips is None:
        await call.message.answer("Ошибка при сканировании домена.")
        return

    # Генерируем граф
    graph_path = generate_full_network_graph(domain, ips, open_ports, server_info)

    # Отправляем картинку
    with open(graph_path, "rb") as photo:
        await call.message.answer_photo(photo=InputFile(photo), caption=f"Граф связей для {domain}")

    # Можно удалить файл, если хочешь
    import os
    os.remove(graph_path)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)