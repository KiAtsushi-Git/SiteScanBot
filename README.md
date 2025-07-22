# 🛰️ SiteScanBot — Телеграм-бот для анализа сайтов и доменов

**SiteScanBot** — Telegram-бот на базе `aiogram`, который позволяет анализировать домены и сайты.

## 📦 Что умеет

- Извлекает IP-адреса из домена (IPv4 и IPv6)
- Получает DNS-записи: A, AAAA, MX, NS, TXT
- Сканирует открытые порты
- Показывает информацию о сервере (страна, город, провайдер)
- Строит граф связей: Домен → IP → Порты → Город/ISP

## 🔧 Установка

```bash
git clone https://github.com/your-username/sitescanbot.git
cd sitescanbot

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Создай файл `dops/config.py` и добавь свой токен Telegram-бота:

```python
BotToken = "your-telegram-bot-token"
```

## 🧠 Используемые библиотеки

- aiogram
- aiohttp
- dnspython
- networkx
- matplotlib

## 📁 Структура проекта

```
main.py                 # запуск бота
dops/
  ├─ keyboard.py        # клавиатура бота
  └─ config.py          # настройки и токен
utils/
  ├─ scan.py            # сканирование IP, DNS, портов
  ├─ graph.py           # генерация графа PNG
  └─ reafact.py         # парсинг и утилиты
```

## 📄 Лицензия

Проект распространяется по лицензии MIT.

---
### Автор

| **Name** | Faraday |
|-------------------|---------|
| **Old**          | 15      |
| **Country** | Russian |
| **Nickname** | KiAtsushi |
| **Email** | [kiatsushi@ki.ru.net](mailto:kiatsushi@ki.ru.net) |
| **Telegram** | [@KiAtsushi](https://t.me/KiAtsushi) |

---

### Дополнительная информация

Так как я еще не обладаю большим опытом в этой области а так же в области разработки на Python, я использовал различные интернет-ресурсы и искусственные интеллекты для получения помощи.
