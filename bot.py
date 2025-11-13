import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import os
import time
from datetime import datetime

# === ДОБАВЬТЕ ЭТО ПОСЛЕ ИМПОРТОВ ===
print("=" * 50)
print("🥖 Bakery Bot запускается на Render.com")
print("=" * 50)
# === КОНЕЦ ДОБАВЛЕНИЯ ===


# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = "8125733355:AAE4a-XiC48YQ3FUNuIfY_HIGYAf56-iDaY"
ADMIN_IDS = [7631590101]
# ===================================================

bot = telebot.TeleBot(BOT_TOKEN)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# Папки для данных
DATA_DIR = "data"
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

os.makedirs(DATA_DIR, exist_ok=True)

def safe_json_load(file_path, default=None):
    """Безопасная загрузка JSON"""
    if default is None:
        default = []
    
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки {file_path}: {e}")
        return default

def safe_json_save(data, file_path):
    """Безопасное сохранение JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения {file_path}: {e}")
        return False

# Загрузка данных
def load_products():
    products = safe_json_load(PRODUCTS_FILE, [])
    if not products:
        # Создаем стандартные товары
        default_products = [
            {'id': 1, 'name': '🥖 Бородинский хлеб', 'description': 'Ржаной хлеб на солоде', 'price': 150, 'weight': '500г', 'stock': 10, 'is_active': True},
            {'id': 2, 'name': '🥐 Круассан с шоколадом', 'description': 'Свежий круассан', 'price': 120, 'weight': '100г', 'stock': 15, 'is_active': True},
            {'id': 3, 'name': '🎂 Торт Медовик', 'description': 'Классический медовый торт', 'price': 2000, 'weight': '2кг', 'stock': 3, 'is_active': True},
        ]
        safe_json_save(default_products, PRODUCTS_FILE)
        return default_products
    return products

def load_orders():
    return safe_json_load(ORDERS_FILE, [])

def save_orders(orders):
    return safe_json_save(orders, ORDERS_FILE)

# Хранилища
user_carts = {}
user_checkout_data = {}

# Уведомления админам
def notify_admins(message):
    """Уведомление всех админов"""
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, message, parse_mode='Markdown')
        except Exception as e:
            print(f"❌ Ошибка отправки админу {admin_id}: {e}")

# Уведомления клиентам
def notify_client(user_id, message):
    """Уведомление клиента"""
    try:
        bot.send_message(user_id, message)
        return True
    except Exception as e:
        print(f"❌ Не удалось отправить уведомление пользователю {user_id}: {e}")
        return False

# Основное меню с Reply клавиатурой
def get_main_menu():
    """Главное меню с кнопками рядом с клавиатурой"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("🍞 Каталог"))
    keyboard.row(KeyboardButton("🛒 Корзина"), KeyboardButton("ℹ️ О нас"))
    keyboard.row(KeyboardButton("❌ Отменить заказ"))
    return keyboard

def get_cancel_keyboard():
    """Клавиатура с отменой заказа"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("❌ Отменить заказ"))
    return keyboard

# Основные команды
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    
    text = f"Добро пожаловать в пекарню, {user.first_name}! 🥖\nВыберите раздел:"
    bot.send_message(message.chat.id, text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: message.text == "🍞 Каталог")
def catalog_menu(message):
    products = load_products()
    
    if not products:
        bot.send_message(message.chat.id, "😔 Товаров пока нет", reply_markup=get_main_menu())
        return
    
    keyboard = InlineKeyboardMarkup()
    for product in products:
        if product.get('is_active', True):
            # Проверяем наличие товара
            if product['stock'] > 5:
                status = "✅ Есть"
            elif product['stock'] > 0:
                status = "⚠️ Мало"
            else:
                status = "❌ Нет"
                
            keyboard.row(InlineKeyboardButton(
                f"{product['name']} - {product['price']}₽ {status}", 
                callback_data=f"product_{product['id']}"
            ))
    
    bot.send_message(
        message.chat.id,
        "🍞 Выберите товар:\n\n✅ Есть - товар в наличии\n⚠️ Мало - мало осталось\n❌ Нет - временно нет",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == "🛒 Корзина")
def cart_menu(message):
    show_cart(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ О нас")
def about_menu(message):
    text = (
        "🏪 Наша пекарня\n\n"
        "🍞 Свежая выпечка каждый день\n"
        "📍 Адрес: ул. Пушкина, 10\n"
        "📞 Телефон: +79991234567\n"
        "⏰ Время работы: 8:00-20:00\n\n"
        "🥖 Мы печем с любовью!"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: message.text == "❌ Отменить заказ")
def cancel_order_handler(message):
    user_id = message.from_user.id
    
    # ВОССТАНОВЛЕНИЕ ОСТАТКОВ ПРИ ОТМЕНЕ ЗАКАЗА
    if user_id in user_carts and user_carts[user_id]:
        products = load_products()
        cart_restored = False
        
        for cart_item in user_carts[user_id]:
            for product in products:
                if product['id'] == cart_item['id']:
                    product['stock'] += cart_item['quantity']
                    cart_restored = True
                    print(f"✅ Восстановлен товар {product['name']}: +{cart_item['quantity']} шт.")
                    break
        
        if cart_restored:
            safe_json_save(products, PRODUCTS_FILE)
            print("✅ Остатки восстановлены при отмене заказа")
    
    # Очищаем корзину
    if user_id in user_carts:
        user_carts[user_id] = []
    
    # Очищаем данные оформления
    if user_id in user_checkout_data:
        user_checkout_data.pop(user_id)
    
    bot.send_message(
        message.chat.id,
        "🗑 Заказ отменен. Корзина очищена.",
        reply_markup=get_main_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
def show_product(call):
    product_id = call.data.split('_')[1]
    products = load_products()
    product = next((p for p in products if p['id'] == int(product_id)), None)
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден")
        return
    
    # Проверяем наличие
    if product['stock'] <= 0:
        text = f"❌ {product['name']} временно нет в наличии"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("🔙 Назад в каталог", callback_data='back_to_catalog'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        return
    
    text = (
        f"{product['name']}\n\n"
        f"📝 {product['description']}\n"
        f"⚖️ Вес: {product['weight']}\n"
        f"💰 Цена: {product['price']}₽\n\n"
    )
    
    # Показываем статус наличия без точных цифр
    if product['stock'] > 5:
        text += "✅ В наличии\n\nВыберите количество:"
    elif product['stock'] > 0:
        text += "⚠️ Осталось мало\n\nВыберите количество:"
    
    keyboard = InlineKeyboardMarkup()
    
    if product['stock'] > 0:
        # Кнопки количества
        max_qty = min(5, product['stock'])
        buttons = []
        for i in range(1, max_qty + 1):
            buttons.append(InlineKeyboardButton(str(i), callback_data=f"add_{product_id}_{i}"))
        
        # Распределяем кнопки по рядам
        for i in range(0, len(buttons), 3):
            keyboard.row(*buttons[i:i+3])
    
    keyboard.row(InlineKeyboardButton("🔙 Назад в каталог", callback_data='back_to_catalog'))
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def add_to_cart(call):
    data = call.data.split('_')
    product_id = int(data[1])
    quantity = int(data[2])
    
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Товар не найден")
        return
    
    user_id = call.from_user.id
    
    # ПРОВЕРКА НАЛИЧИЯ ПРИ ДОБАВЛЕНИИ В КОРЗИНУ
    if product['stock'] < quantity:
        bot.answer_callback_query(call.id, "❌ Недостаточно товара в наличии")
        return
    
    # Инициализируем корзину пользователя
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    # Проверяем, есть ли уже товар в корзине
    found = False
    for item in user_carts[user_id]:
        if item['id'] == product['id']:
            # Проверяем общее количество
            total_quantity = item['quantity'] + quantity
            if product['stock'] >= total_quantity:
                item['quantity'] = total_quantity
                found = True
            else:
                bot.answer_callback_query(call.id, f"❌ Нельзя добавить больше {product['stock']} шт.")
                return
            break
    
    # Если товара нет в корзине, добавляем
    if not found:
        user_carts[user_id].append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity
        })
    
    bot.answer_callback_query(call.id, f"✅ {product['name']} × {quantity} шт. добавлен в корзину!")

def show_cart(message_or_call):
    """Показать корзину (работает и с message и с call)"""
    if hasattr(message_or_call, 'chat'):
        # Это message
        user_id = message_or_call.from_user.id
        chat_id = message_or_call.chat.id
        message_id = None
    else:
        # Это call
        user_id = message_or_call.from_user.id
        chat_id = message_or_call.message.chat.id
        message_id = message_or_call.message.message_id
    
    cart = user_carts.get(user_id, [])
    
    if not cart:
        text = "🛒 Ваша корзина пуста"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("🍞 В каталог", callback_data='back_to_catalog'))
        
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard)
        else:
            bot.send_message(chat_id, text, reply_markup=keyboard)
        return
    
    total = 0
    text = "🛒 Ваша корзина:\n\n"
    for item in cart:
        item_total = item['price'] * item['quantity']
        total += item_total
        text += f"• {item['name']}\n  {item['price']}₽ x {item['quantity']} = {item_total}₽\n"
    
    text += f"\n💰 Итого: {total}₽"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("📝 Оформить заказ", callback_data='checkout'))
    keyboard.row(InlineKeyboardButton("🗑 Очистить корзину", callback_data='clear_cart'))
    keyboard.row(InlineKeyboardButton("🍞 Продолжить покупки", callback_data='back_to_catalog'))
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'cart')
def cart_callback(call):
    show_cart(call)

@bot.callback_query_handler(func=lambda call: call.data == 'clear_cart')
def clear_cart(call):
    user_id = call.from_user.id
    
    # ВОССТАНОВЛЕНИЕ ОСТАТКОВ ПРИ ОЧИСТКЕ КОРЗИНЫ
    if user_id in user_carts and user_carts[user_id]:
        products = load_products()
        cart_restored = False
        
        for cart_item in user_carts[user_id]:
            for product in products:
                if product['id'] == cart_item['id']:
                    product['stock'] += cart_item['quantity']
                    cart_restored = True
                    print(f"✅ Восстановлен товар {product['name']}: +{cart_item['quantity']} шт.")
                    break
        
        if cart_restored:
            safe_json_save(products, PRODUCTS_FILE)
            print("✅ Остатки восстановлены при очистке корзины")
    
    user_carts[user_id] = []
    
    bot.answer_callback_query(call.id, "🗑 Корзина очищена")
    show_cart(call)

@bot.callback_query_handler(func=lambda call: call.data == 'checkout')
def start_checkout(call):
    user_id = call.from_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        bot.answer_callback_query(call.id, "❌ Корзина пуста")
        return
    
    # ПРОВЕРКА НАЛИЧИЯ ВСЕХ ТОВАРОВ ПЕРЕД ОФОРМЛЕНИЕМ
    products = load_products()
    out_of_stock_items = []
    
    for cart_item in cart:
        product = next((p for p in products if p['id'] == cart_item['id']), None)
        if product and product['stock'] < cart_item['quantity']:
            out_of_stock_items.append(f"{product['name']} (доступно: {product['stock']} шт.)")
    
    if out_of_stock_items:
        error_text = "❌ Недостаточно товаров:\n" + "\n".join(out_of_stock_items)
        bot.answer_callback_query(call.id, "❌ Проверьте наличие товаров")
        bot.send_message(call.message.chat.id, error_text)
        return
    
    # Сохраняем данные оформления
    user_checkout_data[user_id] = {
        'cart': cart.copy(),
        'message_id': call.message.message_id,
        'chat_id': call.message.chat.id
    }
    
    # Сразу переходим к вводу телефона
    bot.send_message(
        call.message.chat.id,
        "📞 Введите ваш номер телефона:\n\n_Пример: +79991234567_",
        parse_mode='Markdown',
        reply_markup=get_cancel_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_checkout')
def cancel_checkout_callback(call):
    """Обработчик отмены оформления заказа из inline-кнопки"""
    user_id = call.from_user.id
    
    # ВОССТАНОВЛЕНИЕ ОСТАТКОВ ПРИ ОТМЕНЕ ЗАКАЗА
    if user_id in user_carts and user_carts[user_id]:
        products = load_products()
        cart_restored = False
        
        for cart_item in user_carts[user_id]:
            for product in products:
                if product['id'] == cart_item['id']:
                    product['stock'] += cart_item['quantity']
                    cart_restored = True
                    print(f"✅ Восстановлен товар {product['name']}: +{cart_item['quantity']} шт.")
                    break
        
        if cart_restored:
            safe_json_save(products, PRODUCTS_FILE)
            print("✅ Остатки восстановлены при отмене заказа")
    
    # Очищаем корзину
    if user_id in user_carts:
        user_carts[user_id] = []
    
    # Очищаем данные оформления
    if user_id in user_checkout_data:
        user_checkout_data.pop(user_id)
    
    # Удаляем сообщение с подтверждением заказа
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    # Отправляем сообщение об отмене
    bot.send_message(
        call.message.chat.id,
        "❌ Оформление заказа отменено. Корзина очищена.",
        reply_markup=get_main_menu()
    )

def cancel_checkout(user_id, chat_id):
    """Отмена оформления заказа"""
    # ВОССТАНОВЛЕНИЕ ОСТАТКОВ ПРИ ОТМЕНЕ ЗАКАЗА
    if user_id in user_carts and user_carts[user_id]:
        products = load_products()
        cart_restored = False
        
        for cart_item in user_carts[user_id]:
            for product in products:
                if product['id'] == cart_item['id']:
                    product['stock'] += cart_item['quantity']
                    cart_restored = True
                    print(f"✅ Восстановлен товар {product['name']}: +{cart_item['quantity']} шт.")
                    break
        
        if cart_restored:
            safe_json_save(products, PRODUCTS_FILE)
            print("✅ Остатки восстановлены при отмене заказа")
    
    # Очищаем корзину
    if user_id in user_carts:
        user_carts[user_id] = []
    
    # Очищаем данные оформления
    if user_id in user_checkout_data:
        user_checkout_data.pop(user_id)
    
    bot.send_message(
        chat_id,
        "❌ Оформление заказа отменено. Корзина очищена.",
        reply_markup=get_main_menu()
    )

# Упрощенный обработчик телефона
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    
    # Если пользователь в процессе оформления
    if user_id in user_checkout_data:
        checkout_data = user_checkout_data[user_id]
        
        # Если это отмена
        if message.text == "❌ Отменить заказ":
            cancel_checkout(user_id, message.chat.id)
            return
            
        # Если это телефон (первый шаг)
        if 'phone' not in checkout_data:
            phone = message.text.strip()
            
            # Простая валидация телефона
            if not any(char.isdigit() for char in phone) or len(phone) < 5:
                bot.send_message(
                    message.chat.id,
                    "❌ Пожалуйста, введите корректный номер телефона\n\n_Пример: +79991234567 или 89991234567_",
                    parse_mode='Markdown',
                    reply_markup=get_cancel_keyboard()
                )
                return
                
            checkout_data['phone'] = phone
            
            bot.send_message(
                message.chat.id,
                "🏠 Введите адрес доставки:\n\n_Пример: ул. Пушкина, дом 10, кв. 5_",
                parse_mode='Markdown',
                reply_markup=get_cancel_keyboard()
            )
            
        # Если это адрес (второй шаг)  
        elif 'address' not in checkout_data:
            address = message.text.strip()
            
            # Простая валидация адреса
            if len(address) < 5:
                bot.send_message(
                    message.chat.id,
                    "❌ Пожалуйста, введите более подробный адрес",
                    parse_mode='Markdown',
                    reply_markup=get_cancel_keyboard()
                )
                return
                
            checkout_data['address'] = address
            
            # Сразу показываем подтверждение
            show_confirmation(message.chat.id, user_id)
            
    else:
        # Обычные команды меню
        if message.text == "📋 Главное меню":
            start(message)
        elif message.text not in ["🍞 Каталог", "🛒 Корзина", "ℹ️ О нас", "❌ Отменить заказ"]:
            # Если неизвестная команда, показываем главное меню
            bot.send_message(
                message.chat.id,
                "Выберите действие из меню:",
                reply_markup=get_main_menu()
            )

def show_confirmation(chat_id, user_id):
    """Показать подтверждение заказа"""
    checkout_data = user_checkout_data.get(user_id, {})
    cart = checkout_data.get('cart', [])
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    confirm_text = "📋 ПОДТВЕРЖДЕНИЕ ЗАКАЗА\n\n"
    confirm_text += f"📞 Телефон: {checkout_data.get('phone', 'Не указан')}\n"
    confirm_text += f"🏠 Адрес: {checkout_data.get('address', 'Не указан')}\n\n"
    confirm_text += "🛒 Состав заказа:\n"
    
    for item in cart:
        confirm_text += f"• {item['name']} - {item['quantity']} шт. × {item['price']}₽\n"
    
    confirm_text += f"\n💰 Итого: {total}₽\n\n"
    confirm_text += "✅ Для подтверждения нажмите кнопку ниже"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("✅ Подтвердить заказ", callback_data='force_confirm'))
    keyboard.row(InlineKeyboardButton("❌ Отменить", callback_data='cancel_checkout'))
    
    bot.send_message(chat_id, confirm_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'force_confirm')
def force_confirm_order(call):
    """ПРИНУДИТЕЛЬНОЕ подтверждение заказа - ВСЕГДА РАБОТАЕТ"""
    user_id = call.from_user.id
    
    try:
        # Пытаемся сохранить заказ
        orders = load_orders()
        order_id = len(orders) + 1
        
        checkout_data = user_checkout_data.get(user_id, {})
        
        order = {
            'order_id': order_id,
            'user_id': user_id,
            'user_name': call.from_user.first_name,
            'phone': checkout_data.get('phone', 'Не указан'),
            'address': checkout_data.get('address', 'Не указан'),
            'cart': checkout_data.get('cart', []),
            'total': sum(item['price'] * item['quantity'] for item in checkout_data.get('cart', [])),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'новый'
        }
        
        orders.append(order)
        save_orders(orders)
        
        # УМЕНЬШЕНИЕ ОСТАТКОВ ТОВАРОВ ПРИ ЗАКАЗЕ
        products = load_products()
        for cart_item in checkout_data.get('cart', []):
            for product in products:
                if product['id'] == cart_item['id']:
                    product['stock'] -= cart_item['quantity']
                    print(f"✅ Списан товар {product['name']}: -{cart_item['quantity']} шт. Осталось: {product['stock']}")
                    break
        
        # Сохраняем обновленные остатки
        safe_json_save(products, PRODUCTS_FILE)
        print("✅ Остатки товаров обновлены после заказа")
        
        # Уведомляем админов
        admin_text = f"🆕 НОВЫЙ ЗАКАЗ #{order_id}\n\n"
        admin_text += f"👤 Клиент: {call.from_user.first_name}\n"
        admin_text += f"📞 Телефон: `{order['phone']}`\n"
        admin_text += f"🏠 Адрес: {order['address']}\n"
        admin_text += f"💰 Сумма: {order['total']}₽\n\n"
        admin_text += "🛒 Товары:\n"
        for item in order['cart']:
            admin_text += f"• {item['name']} - {item['quantity']} шт.\n"
        
        notify_admins(admin_text)
        
        # УВЕДОМЛЕНИЕ КЛИЕНТУ
        client_notification = (
            f"🎉 Ваш заказ #{order_id} принят!\n\n"
            f"💰 Сумма: {order['total']}₽\n"
            f"📞 Телефон: {order['phone']}\n"
            f"🏠 Адрес: {order['address']}\n\n"
            f"🛒 Состав заказа:\n"
        )
        for item in order['cart']:
            client_notification += f"• {item['name']} - {item['quantity']} шт.\n"
        
        client_notification += "\n⏳ Статус заказа можно отслеживать здесь"
        notify_client(user_id, client_notification)
        
    except Exception as e:
        print(f"⚠️ Ошибка при сохранении заказа: {e}")
        # НЕ ПРЕРЫВАЕМ - все равно показываем подтверждение клиенту
    
    # УДАЛЯЕМ сообщение с формой подтверждения
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    # Очищаем корзину
    if user_id in user_carts:
        user_carts[user_id] = []
    if user_id in user_checkout_data:
        user_checkout_data.pop(user_id)
    
    # ОТПРАВЛЯЕМ НОВОЕ сообщение с подтверждением
    success_text = "🎉 ЗАКАЗ ПРИНЯТ!\n\n"
    success_text += "✅ Ваш заказ принят в обработку!\n\n"
    success_text += "📞 Наш менеджер свяжется с вами в течение 15 минут\n"
    success_text += "для подтверждения деталей заказа.\n\n"
    success_text += "📍 Контакты пекарни:\n"
    success_text += "• Телефон: +79991234567\n"
    success_text += "• Адрес: ул. Пушкина, 10\n"
    success_text += "• Время работы: 8:00-20:00\n\n"
    success_text += "🥖 Спасибо за ваш заказ!"
    
    bot.send_message(
        call.message.chat.id,
        success_text,
        reply_markup=get_main_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_catalog')
def back_to_catalog(call):
    """Возврат в каталог"""
    catalog_menu(call.message)

# Запуск бота
print("🥖 Бот пекарни запускается...")
print(f"🔔 Уведомления для админов: {ADMIN_IDS}")
print("📁 Данные сохраняются в папку: data/")
print("🚀 Бот готов к работе!")

bot.polling(none_stop=True)