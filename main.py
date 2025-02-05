import asyncio
from datetime import datetime
import time
from aiogram import F
from aiogram.types import Message, ContentType
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models import *
from utils import SheetsAPI
from config import *


dp = Dispatcher()
sheets = SheetsAPI(CRED)

open('logging.log', 'wb')
def log(*args):
    out = ' '.join([str(x) for x in [time.strftime("%d-%H:%M:%S"), f'[I]:', *args]])
    print(out)
    open('logging.log', 'a', -1, 'utf8').write(out + '\n')


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    chat_id = message.chat.id
    log(chat_id, '-> /start')
    defaults={
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'language_code': message.from_user.language_code,
        'last_activity': datetime.now()
    }
    user, created = User.get_or_create(user_id=message.from_user.id, defaults=defaults)
    if not created:
        for key, value in defaults.items():
            setattr(user, key, value)
        user.save()

    if chat_id in ADMIN_IDS:
        main_menu = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить пример работы", callback_data="add_portfolio")],
                [InlineKeyboardButton(text="Логи", callback_data="logs")],
                [InlineKeyboardButton(text="Статистика нажатия кнопок", callback_data="stats")]
            ]
        )
        await message.answer("Панель админстратора", reply_markup=main_menu)
    else:
        main_menu = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="О компании", callback_data="about")],
                [InlineKeyboardButton(text="Заказать бота", callback_data="order")],
                [InlineKeyboardButton(text="Соц-сети", callback_data="socials")],
                [InlineKeyboardButton(text="Примеры работ", callback_data="examples")]
            ]
        )
        await message.answer("Привет! Я AdFMBot. Чем могу помочь?", reply_markup=main_menu)


@dp.message(F.content_type.in_([ContentType.PHOTO]))
async def handle_albums(message: Message):
    chat_id = message.chat.id
    log(chat_id, '-> [PHOTO]:', message.photo[-1].file_id)
    if chat_id in ADMIN_IDS:
        file_id = message.photo[-1].file_id
        Example.create(description=message.caption, photo=file_id)
        await bot.send_message(chat_id, 'Пример работы добавлен')


@dp.message()
async def message_handler(message: Message):
    chat_id = message.chat.id
    log(chat_id, '-> [TEXT]:', message.text[:100])
    if chat_id in ADMIN_IDS:
        Example.create(description=message.text)
        await bot.send_message(chat_id, 'Пример работы добавлен')
    
    elif len(message.text) > 10:
        sheets.update_data(chat_id, message.text)
        await bot.send_message(chat_id, 'Ваша заявка принята. Мы с вами скоро свяжемся.')
        for admin in ADMIN_IDS:
            await bot.send_message(admin, (
                'Поступила заявка от клиента '+
                f'{message.from_user.first_name} [{message.from_user.username if message.from_user.username else message.from_user.id}]:\n'+
                '----------------' +
                message.text +
                '----------------'
            ))
            

@dp.callback_query()
async def about_company(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    log(chat_id, '-> [BUTTON]:', callback_query.data)
    if callback_query.data == 'about':
        btn, created = ButtonStat.get_or_create(button_text='О компании')
        btn.click_count += 1
        btn.save()
        
        text = (
            'AdFMBot — Создаем Telegram-ботов, которые работают на ваш бизнес!\n'
            '👥 Кто мы?\n'
            'Команда из 5 молодых и целеустремленных разработчиков. Мы используем современные технологии, включая ИИ, чтобы решать ваши бизнес-задачи. Работаем на Python 📱 (фремйворк Aiogram)\n\n'
            '❓Почему выбирают нас❓\n'
            '✔️Подход Z-ов — свежие идеи, актуальные технологии и нестандартные решения нового поколения Z.\n'
            '✔️ Честные цены — максимум пользы за разумный бюджет.\n'
            '✔️ Опыт — каждый специалист имеет опыт разработки телеграмм-ботов свыше 3 лет\n'
            '✔️ Личное отношение — работаем с вашими задачами, как с нашими собственными.\n'
            '✔️ Скорость — создаем качественных ботов быстро и без задержек.\n'
            '✔️ Поддержка — ваш бот в надежных руках даже после завершения проекта.'
        )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, text)


    elif callback_query.data == 'order':
        btn, created = ButtonStat.get_or_create(button_text='Заказать бота')
        btn.click_count += 1
        btn.save()

        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите описание желаемого бота:")


    elif callback_query.data == 'socials':
        btn, created = ButtonStat.get_or_create(button_text='Соц-сети')
        btn.click_count += 1
        btn.save()

        text = (
            "Наши соцсети:\n"
            "🔹 Telegram-канал: https://t.me/AdFMBot_chanel\n"
            "🔹 Kwork: https://kwork.ru/user/alexei_adfmbot\n"
            "🔹 Авито: https://www.avito.ru/novosibirsk/predlozheniya_uslug/sotrudnik_s_iskusstvennym_intellektom_na_avitotg_4881725943"
        )
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, text)


    elif callback_query.data == 'examples':
        btn, created = ButtonStat.get_or_create(button_text='Примеры работ')
        btn.click_count += 1
        btn.save()
        
        await bot.answer_callback_query(callback_query.id)
        examples = Example.select()
        if examples.count() == 0:
            await bot.send_message(callback_query.from_user.id, "Примеры работ пока не добавлены.")

        for example in Example.select():
            if example.photo:
                await bot.send_photo(chat_id, example.photo, caption=example.description)
            else:
                await bot.send_message(callback_query.from_user.id, example.description)


    elif callback_query.data == 'add_portfolio':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Отправьте примера работы в текстовом формате или фото обложка с описанием")


    elif callback_query.data == 'logs':
        logs = open('logging.log', 'r', -1, encoding='utf8').readlines()
        await bot.send_message(chat_id, ''.join(logs[-50:]))


    elif callback_query.data == 'stats':
        text = ''
        for button in ButtonStat.select():
            text += f'[{button.button_text}] - {button.click_count}\n'

        await bot.send_message(callback_query.from_user.id, text if text else 'Статистика ещё пуст!')


if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    asyncio.run(dp.start_polling(bot))
