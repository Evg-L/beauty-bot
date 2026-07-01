import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = int(os.getenv('VK_GROUP_ID'))

# Настройки салона
SALON_NAME = "🌟 Салон Красоты 'Beauty'"
SALON_PHONE = "+7 (999) 123-45-67"
SALON_ADDRESS = "ул. Центральная, д. 10"

# Услуги и цены
SERVICES = {
    'стрижка': {'price': '1500 руб.', 'duration': '60 мин'},
    'маникюр': {'price': '2000 руб.', 'duration': '90 мин'},
    'педикюр': {'price': '2500 руб.', 'duration': '120 мин'},
    'окрашивание': {'price': '3000 руб.', 'duration': '120 мин'},
    'укладка': {'price': '1000 руб.', 'duration': '45 мин'}
}

# Рабочие часы (можно настроить)
WORK_HOURS = {
    'start': 10,  # 10:00
    'end': 20     # 20:00
}