import logging
from APIs import TG_API, OWM_API
from aiogram import Dispatcher, Bot, types, executor
import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TG_API)
dp = Dispatcher(bot)

start_kb = InlineKeyboardMarkup(row_width=1)
start_kb.add(InlineKeyboardButton(text="Новосибирск", callback_data='getNovosibirskWeather'))\
    .row(InlineKeyboardButton(text="Москва", callback_data='getMoscowWeather'), InlineKeyboardButton(text="Санкт-Петербург", callback_data='getLeningradWeather'))\
    .add(InlineKeyboardButton(text="Ростов-на-Дону", callback_data='getRostov-on-donWeather'))

back_to_menu_kb = InlineKeyboardMarkup(row_width=1)
back_to_menu_kb.add(InlineKeyboardButton(text="Назад в меню", callback_data='backToMenu'))


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"Привет, Вы можете узнать погоду в городе:", reply_markup=start_kb)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer(f"Для работы бота нужно всего лишь нажимать на кнопки, такие как чуть ниже", reply_markup=back_to_menu_kb)


@dp.message_handler(commands=['author'])
async def author(message: types.Message):
    await message.answer(f"Я Николай Набоков @nnabokov, разработчик данного бота", reply_markup=back_to_menu_kb)


@dp.callback_query_handler(Text('backToMenu'))
async def backToMenu(callback: types.CallbackQuery):
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=f"Рад снова Вас видеть\nВы можете узнать погоду в городе: ",
        reply_markup=start_kb
    )
    await callback.answer()

@dp.callback_query_handler(Text(startswith='get') and Text(endswith='Weather'))
async def getWeather(callback: types.CallbackQuery):
    city = callback.data[3:-7]
    data = requests.get('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=' + OWM_API).json()

    data['main']['temp_min'] = int(data['main']['temp_min'] + (0.5 if data['main']['temp_min'] > 0 else -0.5))
    data['main']['temp_max'] = int(data['main']['temp_max'] + (0.5 if data['main']['temp_max'] > 0 else -0.5))
    data['wind']['speed'] = int(data['wind']['speed'] + (0.5 if data['wind']['speed'] > 0 else -0.5))
    data['main']['feels_like'] = int(data['main']['feels_like'] + (0.5 if data['main']['feels_like'] > 0 else -0.5))

    temperature = f"от {data['main']['temp_min']} до {data['main']['temp_max']}" if {data['main']['temp_min']} != {data['main']['temp_max']} else f"{data['main']['temp_min']}"
    message = f"В городе {data['name']} сейчас {data['weather'][0]['description']}, "\
              f"температура {temperature} по цельсию, " \
              f"но ощущается на {data['main']['feels_like']}. Скорость ветра {data['wind']['speed']} м/с, а облачность {data['clouds']['all']}%."

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=message,
        reply_markup=back_to_menu_kb
        )
    await callback.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)