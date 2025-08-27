import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import json
import os

# Берём данные из GitHub Secrets
API_TOKEN = os.getenv('API_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID'))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("Оставить заявку"))

user_data = {}
COUNTER_FILE = 'counter.json'

def get_next_request_number():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {'counter': 0}
    data['counter'] += 1
    with open(COUNTER_FILE, 'w') as f:
        json.dump(data, f)
    return data['counter']

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот сервиса «Ремонт холодильников Сызрань».\n"
        "Через меня можно оставить заявку на ремонт холодильника.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=kb
    )

@dp.message_handler(lambda message: message.text == "Оставить заявку")
async def start_request(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Введите ваше имя:")

@dp.message_handler(lambda message: message.from_user.id in user_data and 'name' not in user_data[message.from_user.id])
async def get_name(message: types.Message):
    user_data[message.from_user.id]['name'] = message.text
    await message.answer("Введите ваш телефон:")

@dp.message_handler(lambda message: message.from_user.id in user_data and 'phone' not in user_data[message.from_user.id])
async def get_phone(message: types.Message):
    user_data[message.from_user.id]['phone'] = message.text
    await message.answer("Введите адрес для выезда:")

@dp.message_handler(lambda message: message.from_user.id in user_data and 'address' not in user_data[message.from_user.id])
async def get_address(message: types.Message):
    user_data[message.from_user.id]['address'] = message.text
    await message.answer("Опишите проблему с холодильником кратко:")

@dp.message_handler(lambda message: message.from_user.id in user_data and 'problem' not in user_data[message.from_user.id])
async def get_problem(message: types.Message):
    user_data[message.from_user.id]['problem'] = message.text
    data = user_data.pop(message.from_user.id)
    request_number = get_next_request_number()
    text = (
        f"📌 Заявка #{request_number} 📌\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"Проблема: {data['problem']}"
    )
    await bot.send_message(GROUP_ID, text)
    await message.answer(f"✅ Ваша заявка №{request_number} отправлена! Мастер свяжется с вами скоро.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
