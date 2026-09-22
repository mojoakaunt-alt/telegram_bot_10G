
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

from dotenv import load_dotenv
from google_sheet import get_lessons, clear_cache
import os

load_dotenv()

bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher()

TZ = ZoneInfo("Europe/Kyiv")

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Який зараз урок?")],
        [KeyboardButton(text="📅 Сьогодні")],
        [KeyboardButton(text="🔎 Пошук уроку")],
        [KeyboardButton(text="🔄 Оновити розклад")]
    ],
    resize_keyboard=True
)

days = ["Понеділок","Вівторок","Середа","Четвер","Пʼятниця"]

def now():
    return datetime.now(TZ)

def mins(value):
    h, m = value.split(":")
    return int(h)*60+int(m)

def format_lesson(l, title):
    return f"""{title}

📚 {l['Предмет']}
⏰ {l['Початок']} - {l['Кінець']}
👩‍🏫 {l.get('Вчитель','')}

🔗 Zoom:
{l.get('Zoom','')}

🏫 Classroom:
{l.get('Classroom','')}
"""

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Розклад 10-Г\nОберіть дію:", reply_markup=menu)

@dp.message(F.text=="📚 Який зараз урок?")
async def current(message: Message):
    data=get_lessons()
    day=days[now().weekday()]
    t=now().hour*60+now().minute

    today=[x for x in data if x["День"]==day]

    for l in today:
        if mins(l["Початок"]) <= t <= mins(l["Кінець"]):
            await message.answer(format_lesson(l,"📚 Зараз урок:"))
            return

    for l in today:
        if mins(l["Початок"]) > t:
            await message.answer(format_lesson(l,"☕ Зараз перерва\n\nНаступний урок:"))
            return

    await message.answer("✅ На сьогодні уроки закінчилися")

@dp.message(F.text=="📅 Сьогодні")
async def today(message: Message):
    day=days[now().weekday()]
    text=f"📅 {day}\n\n"
    for l in get_lessons():
        if l["День"]==day:
            text+=f"{l['№ уроку']}. {l['Предмет']} {l['Початок']}-{l['Кінець']}\n"
    await message.answer(text)

@dp.message(F.text=="🔎 Пошук уроку")
async def search_hint(message: Message):
    await message.answer("Введіть назву предмета:")

@dp.message(F.text=="🔄 Оновити розклад")
async def refresh(message: Message):
    clear_cache()
    await message.answer("✅ Розклад оновлено")

@dp.message()
async def search(message: Message):
    q=message.text.lower()
    for l in get_lessons():
        if q in l["Предмет"].lower():
            await message.answer(format_lesson(l,"🔎 Знайдений урок:"))
            return
    await message.answer("Не знайдено")

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
