from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def get_main_keyboard():
    """Главное меню"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('📋 Услуги', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('📅 Записаться', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('📞 Контакты', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('📝 Мои записи', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('❓ Помощь', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_services_keyboard():
    """Меню услуг"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('✂️ Стрижка', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('💅 Маникюр', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('🦶 Педикюр', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('🎨 Окрашивание', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('💇‍♀️ Укладка', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('⬅️ Назад', color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_appointment_keyboard():
    """Клавиатура для записи"""
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('✅ Подтвердить запись', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('❌ Отменить', color=VkKeyboardColor.NEGATIVE)
    return keyboard

def get_confirm_keyboard():
    """Клавиатура подтверждения"""
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('✅ Да, записаться', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('❌ Нет, отмена', color=VkKeyboardColor.NEGATIVE)
    return keyboard

def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('❌ Отменить запись', color=VkKeyboardColor.NEGATIVE)
    return keyboard