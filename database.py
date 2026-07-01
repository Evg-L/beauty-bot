import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'beauty_salon.db'


def init_db():
    """Создание таблиц в базе данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            registered_at TEXT
        )
    ''')

    # Таблица записей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            date TEXT,
            time TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()


def get_user(user_id):
    """Получить данные пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def save_user(user_id, first_name, last_name=None, phone=None):
    """Сохранить пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, first_name, last_name, phone, registered_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, first_name, last_name, phone, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def save_appointment(user_id, service, date, time):
    """Сохранить запись"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO appointments (user_id, service, date, time, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, service, date, time, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_appointments(user_id=None):
    """Получить записи (для конкретного пользователя или все)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if user_id:
        cursor.execute('''
            SELECT * FROM appointments 
            WHERE user_id = ? AND status = 'active'
            ORDER BY date, time
        ''', (user_id,))
    else:
        cursor.execute('''
            SELECT * FROM appointments 
            WHERE status = 'active'
            ORDER BY date, time
        ''')

    appointments = cursor.fetchall()
    conn.close()
    return appointments


def get_free_slots(date):
    """Получить свободные слоты на определённую дату"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Получаем занятые слоты
    cursor.execute('''
        SELECT time FROM appointments 
        WHERE date = ? AND status = 'active'
    ''', (date,))

    booked = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Генерируем все слоты с 10:00 до 20:00 с интервалом в 60 минут
    all_slots = []
    for hour in range(10, 20):
        time_str = f"{hour:02d}:00"
        all_slots.append(time_str)

    # Возвращаем свободные слоты
    free_slots = [slot for slot in all_slots if slot not in booked]
    return free_slots


def cancel_appointment(appointment_id, user_id):
    """Отменить запись (только для владельца)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE appointments 
        SET status = 'cancelled' 
        WHERE id = ? AND user_id = ?
    ''', (appointment_id, user_id))

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_available_dates(days_ahead=14):
    """Получить доступные даты для записи"""
    dates = []
    today = datetime.now().date()

    for i in range(days_ahead):
        date = today + timedelta(days=i)
        date_str = date.strftime('%d.%m.%Y')
        free_slots = get_free_slots(date_str)
        if free_slots:  # Если есть свободные слоты
            dates.append(date_str)

    return dates


# Инициализируем базу данных при импорте
init_db()