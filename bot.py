import threading
import time
import requests

def keep_alive():
    url = "https://beautylot.onrender.com"
    while True:
        try:
            requests.get(url)
            print("💓 Пинг отправлен")
        except:
            pass
        time.sleep(600)  # каждые 10 минут

# Запускаем в отдельном потоке
threading.Thread(target=keep_alive, daemon=True).start()

#Пинг бота/

from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import os
import re
from datetime import datetime

from config import *
from database import *
from keyboards import *


import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Минимальный веб-сервер для Render
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')

def run_server():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

# Запускаем сервер в фоновом потоке
threading.Thread(target=run_server, daemon=True).start()


load_dotenv()

TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = int(os.getenv('VK_GROUP_ID'))

# Инициализация бота
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# Хранилище состояний пользователей (временное)
user_states = {}


# {user_id: {'step': 'waiting_service', 'service': 'стрижка', 'date': '...', 'time': '...'}}

def send_message(user_id, message, keyboard=None):
    """Отправить сообщение с клавиатурой"""
    vk.messages.send(
        peer_id=user_id,
        message=message,
        random_id=0,
        keyboard=keyboard.get_keyboard() if keyboard else None
    )


def send_text_message(user_id, message):
    """Отправить сообщение без клавиатуры"""
    vk.messages.send(
        peer_id=user_id,
        message=message,
        random_id=0
    )


def get_user_name(user_id):
    """Получить имя пользователя"""
    try:
        user_info = vk.users.get(user_ids=user_id)[0]
        return user_info.get('first_name', 'Друг')
    except:
        return 'Друг'


def format_service_info(service_name):
    """Форматировать информацию об услуге"""
    if service_name in SERVICES:
        info = SERVICES[service_name]
        return f"💇‍♀️ {service_name.capitalize()}\n💰 Цена: {info['price']}\n⏱ Длительность: {info['duration']}"
    return "Услуга не найдена"


def handle_start_command(user_id):
    """Обработка команды /start"""
    user_name = get_user_name(user_id)

    # Сохраняем пользователя в БД
    save_user(user_id, user_name)

    message = f"""🌟 Здравствуйте, {user_name}!

Добро пожаловать в салон красоты 'Beauty'! ✨

Я ваш виртуальный ассистент. Чем могу помочь?

📋 Просмотреть услуги и цены
📅 Записаться на процедуру
📞 Получить контакты салона
📝 Посмотреть мои записи

Выберите действие из меню ниже 👇"""

    send_message(user_id, message, get_main_keyboard())


def handle_services(user_id):
    """Показать список услуг"""
    message = "📋 Наши услуги:\n\n"

    for service, info in SERVICES.items():
        message += f"✂️ {service.capitalize()}\n"
        message += f"   💰 {info['price']}\n"
        message += f"   ⏱ {info['duration']}\n\n"

    message += "Выберите услугу для получения подробной информации и записи:"

    send_message(user_id, message, get_services_keyboard())


def handle_service_detail(user_id, service):
    """Показать подробности услуги"""
    service_lower = service.lower()

    if service_lower in SERVICES:
        info = format_service_info(service_lower)
        message = f"📌 {info}\n\nХотите записаться на эту услугу?"

        # Сохраняем выбранную услугу в состояние
        if user_id not in user_states:
            user_states[user_id] = {}
        user_states[user_id]['service'] = service_lower
        user_states[user_id]['step'] = 'waiting_date'

        send_text_message(user_id, message)
        handle_appointment_date(user_id)
    else:
        message = "❌ Извините, такой услуги нет в нашем прайсе. Выберите из списка:"
        send_message(user_id, message, get_services_keyboard())


def handle_appointment_date(user_id):
    """Выбор даты записи"""
    available_dates = get_available_dates()

    if not available_dates:
        message = "😔 К сожалению, на ближайшие дни нет свободных слотов. Попробуйте позже."
        send_message(user_id, message, get_main_keyboard())
        return

    message = "📅 Доступные даты для записи:\n\n"
    for i, date in enumerate(available_dates, 1):
        message += f"{i}. {date}\n"

    message += "\n📍 Введите номер даты или напишите дату в формате ДД.ММ.ГГГГ"

    user_states[user_id]['step'] = 'waiting_date'
    send_text_message(user_id, message)


def handle_date_selection(user_id, text):
    """Обработка выбора даты"""
    try:
        # Проверяем, если пользователь ввел номер
        if text.isdigit():
            index = int(text) - 1
            available_dates = get_available_dates()
            if 0 <= index < len(available_dates):
                date = available_dates[index]
            else:
                send_text_message(user_id, "❌ Неверный номер. Попробуйте снова:")
                return
        else:
            # Проверяем дату в формате ДД.ММ.ГГГГ
            if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', text):
                send_text_message(user_id, "❌ Неверный формат. Используйте ДД.ММ.ГГГГ")
                return
            date = text

        # Проверяем, есть ли свободные слоты
        free_slots = get_free_slots(date)
        if not free_slots:
            send_text_message(user_id, "❌ На эту дату нет свободных слотов. Выберите другую дату:")
            handle_appointment_date(user_id)
            return

        # Сохраняем дату
        user_states[user_id]['date'] = date
        user_states[user_id]['step'] = 'waiting_time'

        # Показываем свободные слоты
        message = f"🕐 Свободное время на {date}:\n\n"
        for i, slot in enumerate(free_slots, 1):
            message += f"{i}. {slot}\n"

        message += "\n📍 Введите номер времени или время в формате ЧЧ:ММ"
        send_text_message(user_id, message)

    except Exception as e:
        send_text_message(user_id, f"❌ Ошибка: {str(e)}")


def handle_time_selection(user_id, text):
    """Обработка выбора времени"""
    try:
        date = user_states[user_id].get('date')
        if not date:
            send_text_message(user_id, "❌ Ошибка. Пожалуйста, начните запись заново.")
            return

        free_slots = get_free_slots(date)

        # Проверяем выбор
        if text.isdigit():
            index = int(text) - 1
            if 0 <= index < len(free_slots):
                time = free_slots[index]
            else:
                send_text_message(user_id, "❌ Неверный номер. Попробуйте снова:")
                return
        else:
            # Проверяем формат времени
            if not re.match(r'^\d{2}:\d{2}$', text):
                send_text_message(user_id, "❌ Неверный формат. Используйте ЧЧ:ММ")
                return
            if text not in free_slots:
                send_text_message(user_id, "❌ Это время уже занято. Выберите другое:")
                handle_appointment_date(user_id)
                return
            time = text

        # Сохраняем время
        user_states[user_id]['time'] = time
        user_states[user_id]['step'] = 'waiting_confirm'

        # Показываем подтверждение
        service = user_states[user_id].get('service', 'не выбрана')
        service_info = format_service_info(service)

        message = f"""✅ Подтверждение записи:

📋 Услуга: {service.capitalize()}
💰 {SERVICES[service]['price']}
⏱ {SERVICES[service]['duration']}

📅 Дата: {date}
🕐 Время: {time}

📍 {SALON_ADDRESS}
📞 {SALON_PHONE}

Все верно?"""

        send_message(user_id, message, get_confirm_keyboard())

    except Exception as e:
        send_text_message(user_id, f"❌ Ошибка: {str(e)}")


def handle_confirm_appointment(user_id):
    """Подтверждение записи"""
    state = user_states.get(user_id, {})
    service = state.get('service')
    date = state.get('date')
    time = state.get('time')

    if not all([service, date, time]):
        send_text_message(user_id, "❌ Ошибка. Пожалуйста, начните запись заново.")
        return

    # Сохраняем запись в БД
    save_appointment(user_id, service, date, time)

    message = f"""✅ Запись подтверждена!

🌟 Вы записаны на {service.capitalize()}
📅 {date} в {time}

📍 {SALON_ADDRESS}
📞 {SALON_PHONE}

Мы ждем вас! Если нужно отменить запись, напишите 'Отменить запись'."""

    send_message(user_id, message, get_main_keyboard())

    # Очищаем состояние
    user_states.pop(user_id, None)


def handle_my_appointments(user_id):
    """Показать записи пользователя"""
    appointments = get_appointments(user_id)

    if not appointments:
        send_text_message(user_id, "📝 У вас пока нет записей.\n\nНажмите '📅 Записаться', чтобы создать запись.")
        return

    message = "📝 Ваши записи:\n\n"
    for app in appointments:
        message += f"🔹 {app[2].capitalize()}\n"
        message += f"   📅 {app[3]} в {app[4]}\n"
        message += f"   Статус: {'✅ Активна' if app[5] == 'active' else '❌ Отменена'}\n\n"

    message += "Чтобы отменить запись, отправьте 'Отменить запись' и укажите дату."
    send_text_message(user_id, message)


def handle_contacts(user_id):
    """Показать контакты салона"""
    message = f"""📞 Контакты салона:

📍 Адрес: {SALON_ADDRESS}
📱 Телефон: {SALON_PHONE}
🕐 Режим работы: {WORK_HOURS['start']}:00 - {WORK_HOURS['end']}:00

🌟 {SALON_NAME}

Приходите, будем рады вас видеть!"""

    send_message(user_id, message, get_main_keyboard())


def handle_cancel_appointment(user_id, text):
    """Отмена записи"""
    # Пытаемся найти запись по дате
    date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
    if date_match:
        date = date_match.group()

        # Находим запись на эту дату
        appointments = get_appointments(user_id)
        target_app = None
        for app in appointments:
            if app[3] == date and app[5] == 'active':
                target_app = app
                break

        if target_app:
            cancel_appointment(target_app[0], user_id)
            send_text_message(user_id, f"✅ Запись на {target_app[3]} в {target_app[4]} отменена.")
        else:
            send_text_message(user_id, "❌ Запись на эту дату не найдена.")
    else:
        send_text_message(user_id, "❌ Укажите дату в формате ДД.ММ.ГГГГ для отмены записи.")
        send_text_message(user_id, "Пример: Отменить запись 15.05.2024")


def handle_help(user_id):
    """Помощь"""
    message = """❓ Как пользоваться ботом:

1️⃣ Нажмите '📋 Услуги' для просмотра прайса
2️⃣ Нажмите '📅 Записаться' для создания записи
3️⃣ Нажмите '📝 Мои записи' для просмотра ваших записей
4️⃣ Нажмите '📞 Контакты' для получения информации о салоне

Для отмены записи отправьте:
'Отменить запись ДД.ММ.ГГГГ'

Если возникли вопросы, звоните по телефону: {SALON_PHONE}"""

    send_message(user_id, message, get_main_keyboard())


# ========== ГЛАВНЫЙ ЦИКЛ БОТА ==========

print(f"🌟 {SALON_NAME}")
print("✅ Бот-ассистент запущен и ждёт сообщений...")
print("=" * 50)

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        try:
            message = event.object.message
            user_id = message['from_id']
            text = message['text'].strip()

            print(f"📩 Пришло сообщение от {user_id}: {text}")

            # Команда /start
            if text.lower() == '/start':
                handle_start_command(user_id)
                continue

            # Проверяем состояние пользователя (процесс записи)
            if user_id in user_states:
                state = user_states[user_id]
                step = state.get('step')

                if step == 'waiting_date':
                    # Если пользователь нажал "Назад" на клавиатуре услуг
                    if text == '⬅️ Назад':
                        handle_services(user_id)
                        continue

                    # Проверяем, может быть пользователь хочет вернуться
                    if text.lower() in ['назад', 'отмена', 'cancel']:
                        user_states.pop(user_id, None)
                        send_message(user_id, "❌ Запись отменена.", get_main_keyboard())
                        continue

                    handle_date_selection(user_id, text)
                    continue

                elif step == 'waiting_time':
                    if text.lower() in ['назад', 'отмена', 'cancel']:
                        user_states.pop(user_id, None)
                        send_message(user_id, "❌ Запись отменена.", get_main_keyboard())
                        continue

                    handle_time_selection(user_id, text)
                    continue

                elif step == 'waiting_confirm':
                    if text == '✅ Да, записаться':
                        handle_confirm_appointment(user_id)
                    elif text == '❌ Нет, отмена':
                        user_states.pop(user_id, None)
                        send_message(user_id, "❌ Запись отменена.", get_main_keyboard())
                    else:
                        send_text_message(user_id, "❌ Пожалуйста, подтвердите или отмените запись.")
                    continue

            # Обработка основного меню
            if text == '📋 Услуги':
                handle_services(user_id)

            elif text == '📅 Записаться':
                # Проверяем, выбрана ли услуга
                if user_id in user_states and user_states[user_id].get('service'):
                    handle_appointment_date(user_id)
                else:
                    send_text_message(user_id, "📍 Сначала выберите услугу из списка:")
                    handle_services(user_id)

            elif text == '📞 Контакты':
                handle_contacts(user_id)

            elif text == '📝 Мои записи':
                handle_my_appointments(user_id)

            elif text == '❓ Помощь':
                handle_help(user_id)

            elif text == '⬅️ Назад':
                send_message(user_id, "Главное меню:", get_main_keyboard())

            # Обработка выбора услуги
            elif text in ['✂️ Стрижка', '💅 Маникюр', '🦶 Педикюр', '🎨 Окрашивание', '💇‍♀️ Укладка']:
                # Извлекаем название услуги без эмодзи
                service_map = {
                    '✂️ Стрижка': 'стрижка',
                    '💅 Маникюр': 'маникюр',
                    '🦶 Педикюр': 'педикюр',
                    '🎨 Окрашивание': 'окрашивание',
                    '💇‍♀️ Укладка': 'укладка'
                }
                service = service_map.get(text)
                if service:
                    handle_service_detail(user_id, service)

            # Отмена записи
            elif 'отменить запись' in text.lower():
                handle_cancel_appointment(user_id, text)

            # Обработка неизвестной команды
            else:
                message_text = """🤔 Я не понял ваш запрос.

Доступные команды:
/start - Начать работу
📋 Услуги - Показать услуги
📅 Записаться - Создать запись
📝 Мои записи - Посмотреть записи
📞 Контакты - Контакты салона
❓ Помощь - Помощь

Выберите действие из меню или нажмите /start"""

                send_message(user_id, message_text, get_main_keyboard())

        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            try:
                send_text_message(user_id, f"⚠️ Произошла ошибка. Пожалуйста, попробуйте снова.")
            except:
                pass
