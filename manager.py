import customtkinter as ctk
import json
import os
import threading
import time
from datetime import datetime, timedelta
import winsound
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('Agg')

class BakeryManager:
    def __init__(self):
        # Настройка тёмной цветовой темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Кастомная тёмная цветовая схема
        self.colors = {
            "primary": "#2D2D2D",      # Тёмно-серый основной
            "primary_dark": "#1A1A1A", # Почти чёрный
            "primary_light": "#404040", # Светло-серый
            "bg_light": "#1E1E1E",     # Тёмный фон
            "bg_lighter": "#252525",   # Светлее тёмный
            "text_dark": "#E0E0E0",    # Светлый текст
            "text_light": "#B0B0B0",   # Серый текст
            "success": "#10B981",      # Изумрудный успех
            "warning": "#F59E0B",      # Янтарный предупреждение
            "error": "#EF4444",        # Красный ошибка
            "accent_blue": "#3B82F6",  # Синий акцент
            "accent_purple": "#8B5CF6", # Фиолетовый акцент
            "accent_gold": "#D4AF37",   # Золотой акцент
            "card_bg": "#2A2A2A",      # Фон карточек
            "hover_bg": "#363636"      # Фон при наведении
        }
        
        # Создание главного окна
        self.root = ctk.CTk()
        self.root.title("🥖 BakeryPro Manager - Premium Edition")
        self.root.geometry("1600x900")
        self.root.configure(fg_color=self.colors["bg_light"])
        
        # Центрирование окна
        self.center_window()
        
        # Инициализация данных
        self.data_dir = "data"
        self.orders_file = os.path.join(self.data_dir, "orders.json")
        self.products_file = os.path.join(self.data_dir, "products.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        self.orders = []
        self.products = []
        self.settings = {}
        self.last_order_count = 0
        self.current_tab = "dashboard"
        self.last_update_time = 0
        self.update_interval = 3
        
        # Загрузка данных
        self.load_data()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Запуск real-time обновлений
        self.start_polling()
        
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = 1600
        height = 900
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def safe_json_load(self, file_path, default=None):
        """Безопасная загрузка JSON"""
        if default is None:
            default = [] if "orders" in file_path or "products" in file_path else {}
        
        if not os.path.exists(file_path):
            return default
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")
            return default
    
    def safe_json_save(self, data, file_path):
        """Безопасное сохранение JSON"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения {file_path}: {e}")
            return False
    
    def load_data(self):
        """Загрузка данных из JSON файлов"""
        try:
            self.orders = self.safe_json_load(self.orders_file, [])
            self.products = self.safe_json_load(self.products_file, [])
            self.settings = self.safe_json_load(self.settings_file, {})
            self.last_order_count = len(self.orders)
            print(f"✅ Загружено {len(self.orders)} заказов, {len(self.products)} товаров")
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
    
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        self.setup_main_content()
        self.update_stats()
    
    def setup_sidebar(self):
        """Левая панель с навигацией в тёмных тонах"""
        sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0, 
                              fg_color=self.colors["primary"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(8, weight=1)
        
        # Заголовок с иконкой
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=120)
        title_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        title_frame.grid_propagate(False)
        
        # Стилизованный заголовок
        title_bg = ctk.CTkFrame(title_frame, corner_radius=15, 
                               fg_color=self.colors["accent_gold"])
        title_bg.pack(fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            title_bg, 
            text="🥖\nBakeryPro", 
            font=ctk.CTkFont(size=24, weight="bold", family="Arial"),
            text_color="#1A1A1A"
        )
        title_label.pack(expand=True)
        
        subtitle_label = ctk.CTkLabel(
            title_bg,
            text="Premium Edition",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2D2D2D"
        )
        subtitle_label.pack(expand=True, pady=(0, 15))
        
        # Кнопки навигации
        buttons = [
            ("📊 Дашборд", "dashboard"),
            ("📋 Заказы", "orders"),
            ("📦 Товары", "products"),
            ("📈 Аналитика", "analytics"),
            ("⚙️ Настройки", "settings"),
        ]
        
        for i, (text, command) in enumerate(buttons, 1):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=lambda cmd=command: self.switch_tab(cmd),
                height=50,
                corner_radius=12,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=self.colors["card_bg"],
                hover_color=self.colors["hover_bg"],
                text_color=self.colors["text_dark"],
                border_width=0
            )
            btn.grid(row=i, column=0, padx=20, pady=8, sticky="ew")
        
        # Статус внизу
        status_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        status_frame.grid(row=9, column=0, padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="🟢 Система активна",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["success"]
        )
        self.status_label.pack()
        
        update_label = ctk.CTkLabel(
            status_frame,
            text="Обновляется в реальном времени",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_light"]
        )
        update_label.pack(pady=(2, 0))
    
    def switch_tab(self, tab_name):
        """Переключение между вкладками"""
        self.current_tab = tab_name
        if tab_name == "dashboard":
            self.show_dashboard()
        elif tab_name == "orders":
            self.show_orders()
        elif tab_name == "products":
            self.show_products()
        elif tab_name == "analytics":
            self.show_analytics()
        elif tab_name == "settings":
            self.show_settings()
    
    def setup_main_content(self):
        """Основная область контента"""
        main_frame = ctk.CTkFrame(self.root, corner_radius=0, 
                                 fg_color=self.colors["bg_light"])
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        self.setup_header(main_frame)
        
        # Контент-фрейм
        self.content_frame = ctk.CTkFrame(main_frame, corner_radius=20,
                                         fg_color=self.colors["card_bg"])
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        self.show_dashboard()
    
    def setup_header(self, parent):
        """Верхняя панель со статистикой"""
        header = ctk.CTkFrame(parent, corner_radius=20, height=120, 
                             fg_color=self.colors["primary"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(5, weight=1)
        header.grid_propagate(False)
        
        # Заголовок
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=2, padx=25, pady=20, sticky="w")
        
        welcome_label = ctk.CTkLabel(
            title_frame,
            text="Добро пожаловать!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        welcome_label.pack(anchor="w")
        
        date_label = ctk.CTkLabel(
            title_frame,
            text=datetime.now().strftime("%d %B %Y"),
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_light"]
        )
        date_label.pack(anchor="w", pady=(2, 0))
        
        # Статистика
        stats_data = [
            ("🆕 Новые", "new_count", self.colors["accent_blue"]),
            ("✅ Принятые", "accepted_count", self.colors["success"]),
            ("💰 Оплата", "payment_count", self.colors["accent_purple"]),
            ("👨‍🍳 Готовятся", "cooking_count", self.colors["warning"]),
            ("🎉 Завершены", "completed_count", self.colors["success"]),
        ]
        
        for i, (text, attr_name, color) in enumerate(stats_data):
            frame = ctk.CTkFrame(header, corner_radius=12, fg_color=color, 
                                height=80, width=140)
            frame.grid(row=0, column=i+2, padx=8, pady=20, sticky="ns")
            frame.grid_propagate(False)
            
            count_label = ctk.CTkLabel(
                frame, 
                text="0", 
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="white"
            )
            count_label.pack(expand=True, pady=(15, 0))
            
            text_label = ctk.CTkLabel(
                frame, 
                text=text, 
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            )
            text_label.pack(expand=True, pady=(0, 15))
            
            setattr(self, attr_name, count_label)
    
    def show_dashboard(self):
        """Показать главный дашборд"""
        self.current_tab = "dashboard"
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Заголовок
        title = ctk.CTkLabel(
            self.content_frame,
            text="📊 Дашборд заказов",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        title.pack(pady=30)
        
        # Мини-статистика
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=20)
        
        today_orders = self.get_today_orders()
        today_revenue = sum(order.get('total', 0) for order in today_orders)
        avg_check = today_revenue // len(today_orders) if today_orders else 0
        
        mini_stats = [
            (f"🛒 Заказов сегодня", f"{len(today_orders)}", self.colors["accent_blue"]),
            (f"💰 Выручка сегодня", f"{today_revenue}₽", self.colors["success"]),
            (f"📦 Средний чек", f"{avg_check}₽", self.colors["accent_purple"]),
        ]
        
        for i, (title, value, color) in enumerate(mini_stats):
            card = ctk.CTkFrame(stats_frame, corner_radius=15, fg_color=color,
                               height=100)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            card.grid_propagate(False)
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color="white"
            ).pack(expand=True, pady=(20, 0))
            
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).pack(expand=True, pady=(0, 20))
        
        # Последние заказы
        self.setup_recent_orders()
    
    def get_today_orders(self):
        """Получить заказы за сегодня"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [order for order in self.orders if order.get('timestamp', '').startswith(today)]
    
    def setup_recent_orders(self):
        """Таблица последних заказов"""
        recent_label = ctk.CTkLabel(
            self.content_frame,
            text="📋 Последние заказы",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_dark"]
        )
        recent_label.pack(pady=(40, 15))
        
        # Создаем скроллируемый фрейм для заказов
        self.orders_table_frame = ctk.CTkScrollableFrame(self.content_frame, 
                                                        height=400, 
                                                        fg_color=self.colors["card_bg"])
        self.orders_table_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.update_orders_table()
    
    def update_orders_table(self):
        """Обновление таблицы заказов"""
        if not hasattr(self, 'orders_table_frame'):
            return
        
        for widget in self.orders_table_frame.winfo_children():
            widget.destroy()
        
        # Заголовки таблицы
        headers_frame = ctk.CTkFrame(self.orders_table_frame, 
                                    fg_color=self.colors["primary_light"], 
                                    height=50)
        headers_frame.pack(fill="x", pady=(0, 10))
        headers_frame.pack_propagate(False)
        
        headers = ["ID", "Клиент", "Телефон", "Сумма", "Статус", "Время", "Действия"]
        widths = [80, 150, 120, 100, 120, 120, 200]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_dark"],
                width=width
            )
            label.grid(row=0, column=i, padx=5, pady=15, sticky="w")
        
        # Сортируем заказы по времени (новые сверху)
        recent_orders = sorted(self.orders, 
                              key=lambda x: x.get('timestamp', ''), 
                              reverse=True)[:10]
        
        for row, order in enumerate(recent_orders):
            self.create_order_row(order, row)
    
    def create_order_row(self, order, row):
        """Создание строки заказа"""
        row_frame = ctk.CTkFrame(self.orders_table_frame, 
                                fg_color=self.colors["card_bg"], 
                                height=60)
        row_frame.pack(fill="x", pady=5)
        row_frame.pack_propagate(False)
        
        # ID заказа
        ctk.CTkLabel(row_frame, 
                    text=f"#{order.get('order_id', 'N/A')}", 
                    font=ctk.CTkFont(weight="bold"), 
                    text_color=self.colors["text_dark"],
                    width=80).grid(row=0, column=0, padx=5, pady=15)
        
        # Имя клиента
        client_name = order.get('user_name', 'Не указан')
        if len(client_name) > 15:
            client_name = client_name[:15] + "..."
        ctk.CTkLabel(row_frame, 
                    text=client_name, 
                    text_color=self.colors["text_light"],
                    width=150).grid(row=0, column=1, padx=5, pady=15)
        
        # Телефон
        phone = order.get('phone', 'N/A')
        ctk.CTkLabel(row_frame, 
                    text=phone, 
                    text_color=self.colors["text_light"],
                    width=120).grid(row=0, column=2, padx=5, pady=15)
        
        # Сумма
        ctk.CTkLabel(row_frame, 
                    text=f"{order.get('total', 0)}₽", 
                    font=ctk.CTkFont(weight="bold"), 
                    text_color=self.colors["success"],
                    width=100).grid(row=0, column=3, padx=5, pady=15)
        
        # Статус
        status_text = order.get('status', 'новый')
        status_color = self.get_status_color(status_text)
        status_label = ctk.CTkLabel(
            row_frame, 
            text=status_text.upper(), 
            text_color="white",
            fg_color=status_color,
            corner_radius=8,
            font=ctk.CTkFont(size=10, weight="bold"),
            width=120
        )
        status_label.grid(row=0, column=4, padx=5, pady=15)
        
        # Время
        time_str = order.get('timestamp', 'N/A')
        short_time = time_str[11:16] if len(time_str) > 16 else time_str
        ctk.CTkLabel(row_frame, 
                    text=short_time, 
                    text_color=self.colors["text_light"],
                    width=120).grid(row=0, column=5, padx=5, pady=15)
        
        # Действия
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=6, padx=5, pady=15, sticky="w")
        
        # Кнопка деталей
        ctk.CTkButton(
            action_frame, 
            text="📋", 
            width=35,
            height=35,
            fg_color=self.colors["accent_blue"],
            hover_color="#2563EB",
            command=lambda oid=order.get('order_id'): self.show_order_details(oid)
        ).pack(side="left", padx=2)
        
        # Кнопки действий в зависимости от статуса
        current_status = order.get('status', 'новый')
        
        if current_status == 'новый':
            ctk.CTkButton(
                action_frame, 
                text="✅ Принять", 
                width=80,
                height=35,
                fg_color=self.colors["success"],
                hover_color="#059669",
                command=lambda oid=order.get('order_id'): self.accept_order(oid)
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                action_frame, 
                text="❌ Отменить", 
                width=80,
                height=35,
                fg_color=self.colors["error"],
                hover_color="#DC2626",
                command=lambda oid=order.get('order_id'): self.cancel_order(oid)
            ).pack(side="left", padx=2)
        
        elif current_status == 'принят':
            ctk.CTkButton(
                action_frame, 
                text="💰 Оплата", 
                width=80,
                height=35,
                fg_color=self.colors["accent_purple"],
                hover_color="#7C3AED",
                command=lambda oid=order.get('order_id'): self.wait_payment(oid)
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                action_frame, 
                text="👨‍🍳 Готовить", 
                width=80,
                height=35,
                fg_color=self.colors["warning"],
                hover_color="#D97706",
                command=lambda oid=order.get('order_id'): self.start_cooking(oid)
            ).pack(side="left", padx=2)
        
        elif current_status == 'ожидает оплаты':
            ctk.CTkButton(
                action_frame, 
                text="💳 Оплачено", 
                width=80,
                height=35,
                fg_color=self.colors["success"],
                hover_color="#059669",
                command=lambda oid=order.get('order_id'): self.mark_paid(oid)
            ).pack(side="left", padx=2)
        
        elif current_status == 'готовится':
            ctk.CTkButton(
                action_frame, 
                text="🚚 Доставка", 
                width=80,
                height=35,
                fg_color=self.colors["accent_blue"],
                hover_color="#2563EB",
                command=lambda oid=order.get('order_id'): self.start_delivery(oid)
            ).pack(side="left", padx=2)
        
        elif current_status == 'в доставке':
            ctk.CTkButton(
                action_frame, 
                text="✅ Завершить", 
                width=80,
                height=35,
                fg_color=self.colors["success"],
                hover_color="#059669",
                command=lambda oid=order.get('order_id'): self.complete_order(oid)
            ).pack(side="left", padx=2)
    
    def get_status_color(self, status):
        """Возвращает цвет для статуса"""
        colors = {
            'новый': self.colors["accent_blue"],
            'принят': self.colors["accent_purple"],
            'ожидает оплаты': self.colors["warning"],
            'готовится': self.colors["accent_gold"],
            'в доставке': "#0EA5E9",  # Голубой
            'завершен': self.colors["success"],
            'отменен': self.colors["error"]
        }
        return colors.get(status, self.colors["text_light"])
    
    def update_stats(self):
        """Обновление статистики в заголовке"""
        new_count = len([o for o in self.orders if o.get('status') == 'новый'])
        accepted_count = len([o for o in self.orders if o.get('status') == 'принят'])
        payment_count = len([o for o in self.orders if o.get('status') == 'ожидает оплаты'])
        cooking_count = len([o for o in self.orders if o.get('status') == 'готовится'])
        completed_count = len([o for o in self.orders if o.get('status') == 'завершен'])
        
        # Анимация изменения чисел
        self.animate_counter(self.new_count, new_count)
        self.animate_counter(self.accepted_count, accepted_count)
        self.animate_counter(self.payment_count, payment_count)
        self.animate_counter(self.cooking_count, cooking_count)
        self.animate_counter(self.completed_count, completed_count)
    
    def animate_counter(self, label, target_value):
        """Анимация счетчика"""
        current_value = int(label.cget("text") or 0)
        
        def update_value():
            nonlocal current_value
            if current_value < target_value:
                current_value += 1
                label.configure(text=str(current_value))
                label.after(30, update_value)
            elif current_value > target_value:
                current_value -= 1
                label.configure(text=str(current_value))
                label.after(30, update_value)
        
        update_value()
    
    def start_polling(self):
        """Запуск real-time обновлений"""
        def poll():
            while True:
                try:
                    current_time = time.time()
                    if current_time - self.last_update_time >= self.update_interval:
                        self.last_update_time = current_time
                        
                        old_count = len(self.orders)
                        old_orders_hash = str(self.orders)
                        
                        self.load_data()
                        new_count = len(self.orders)
                        
                        new_orders_hash = str(self.orders)
                        data_changed = old_orders_hash != new_orders_hash
                        
                        if new_count > old_count and data_changed:
                            new_orders_count = new_count - old_count
                            self.show_notification(f"🆕 {new_orders_count} новый заказ!")
                        
                        if data_changed:
                            self.update_stats()
                            
                            if self.current_tab == "dashboard":
                                self.update_orders_table()
                            elif self.current_tab == "orders":
                                self.update_orders_management()
                            elif self.current_tab == "products":
                                self.update_products_management()
                                
                except Exception as e:
                    print(f"Ошибка обновления: {e}")
                
                time.sleep(1)
        
        thread = threading.Thread(target=poll, daemon=True)
        thread.start()
    
    def show_notification(self, message):
        """Показать уведомление о новом заказе"""
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            pass
        
        # Создаем временное уведомление
        notification = ctk.CTkToplevel(self.root)
        notification.title("Новый заказ!")
        notification.geometry("400x150")
        notification.transient(self.root)
        notification.configure(fg_color=self.colors["accent_blue"])
        
        # Центрирование
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        notification.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(
            notification, 
            text="🎉",
            font=ctk.CTkFont(size=28)
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            notification, 
            text=message,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=5)
        
        ctk.CTkButton(
            notification,
            text="OK",
            command=notification.destroy,
            fg_color="white",
            text_color=self.colors["accent_blue"],
            hover_color="#F0F0F0"
        ).pack(pady=10)
        
        # Автозакрытие через 5 секунд
        notification.after(5000, notification.destroy)
    
    # === УПРАВЛЕНИЕ ЗАКАЗАМИ ===
    
    def accept_order(self, order_id):
        """Принять заказ"""
        if self.update_order_status(order_id, "принят"):
            self.show_success_message(f"Заказ #{order_id} принят!")
    
    def wait_payment(self, order_id):
        """Ожидание оплаты"""
        if self.update_order_status(order_id, "ожидает оплаты"):
            self.show_success_message(f"Заказ #{order_id} ожидает оплаты!")
    
    def start_cooking(self, order_id):
        """Начать готовить"""
        if self.update_order_status(order_id, "готовится"):
            self.show_success_message(f"Заказ #{order_id} начал готовиться!")
    
    def mark_paid(self, order_id):
        """Отметить как оплаченный"""
        if self.update_order_status(order_id, "готовится"):
            self.show_success_message(f"Заказ #{order_id} оплачен!")
    
    def start_delivery(self, order_id):
        """Начать доставку"""
        if self.update_order_status(order_id, "в доставке"):
            self.show_success_message(f"Заказ #{order_id} передан в доставку!")
    
    def complete_order(self, order_id):
        """Завершить заказ"""
        if self.update_order_status(order_id, "завершен"):
            self.show_success_message(f"Заказ #{order_id} завершен!")
    
    def cancel_order(self, order_id):
        """Отменить заказ"""
        result = messagebox.askyesno("Подтверждение", f"Отменить заказ #{order_id}?")
        if result:
            cancel_reason = self.ask_cancel_reason()
            if cancel_reason:
                # ВОССТАНОВЛЕНИЕ ОСТАТКОВ ПРИ ОТМЕНЕ
                order = next((o for o in self.orders if o.get('order_id') == order_id), None)
                if order and order.get('status') != 'отменен':
                    products = self.safe_json_load(self.products_file, [])
                    for cart_item in order.get('cart', []):
                        for product in products:
                            if product['id'] == cart_item['id']:
                                product['stock'] += cart_item['quantity']
                                print(f"✅ Восстановлен товар {product['name']}: +{cart_item['quantity']} шт.")
                                break
                    self.safe_json_save(products, self.products_file)
            
            if self.update_order_status(order_id, "отменен", cancel_reason):
                self.show_success_message(f"Заказ #{order_id} отменен!")
    
    def show_success_message(self, message):
        """Показать сообщение об успехе"""
        messagebox.showinfo("Успех", message)
    
    def ask_cancel_reason(self):
        """Спросить причину отмены"""
        # Упрощенная версия - всегда возвращаем стандартную причину
        return "Отменено администратором"
    
    def send_status_notification(self, order_id, new_status, old_status, cancel_reason=None):
        """Отправка уведомления клиенту о смене статуса"""
        try:
            order = next((o for o in self.orders if o.get('order_id') == order_id), None)
            if not order:
                return
            
            user_id = order.get('user_id')
            if not user_id:
                return
            
            # Тексты уведомлений для разных статусов
            status_messages = {
                'принят': f"✅ Заказ #{order_id} принят в работу! Начинаем готовить ваш заказ.",
                'ожидает оплаты': f"💳 Заказ #{order_id} ожидает оплаты. Сумма: {order.get('total', 0)}₽",
                'готовится': f"👨‍🍳 Заказ #{order_id} готовится! Обычно это занимает 30-60 минут.",
                'в доставке': f"🚚 Заказ #{order_id} передан курьеру! Скоро будем у вас.",
                'завершен': f"🎉 Заказ #{order_id} завершен! Спасибо за покупку!",
                'отменен': f"❌ Заказ #{order_id} отменен. Причина: {cancel_reason or 'не указана'}"
            }
            
            message = status_messages.get(new_status)
            if message:
                # Отправка через Telegram API
                bot_token = "8125733355:AAE4a-XiC48YQ3FUNuIfY_HIGYAf56-iDaY"
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                
                payload = {
                    'chat_id': user_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Уведомление отправлено пользователю {user_id} о статусе {new_status}")
                else:
                    print(f"❌ Ошибка отправки уведомления: {response.text}")
                    
        except Exception as e:
            print(f"❌ Ошибка при отправке уведомления: {e}")
    
    def update_order_status(self, order_id, new_status, cancel_reason=None):
        """Обновить статус заказа"""
        try:
            orders = self.safe_json_load(self.orders_file, [])
            order_updated = False
            old_order = None
            
            for order in orders:
                if order.get('order_id') == order_id:
                    old_order = order.copy()
                    order['status'] = new_status
                    if cancel_reason:
                        order['cancel_reason'] = cancel_reason
                    order_updated = True
                    break
            
            if not order_updated:
                messagebox.showerror("Ошибка", f"Заказ #{order_id} не найден!")
                return False
            
            # Сохраняем
            self.safe_json_save(orders, self.orders_file)
            self.load_data()
            
            # ОТПРАВКА УВЕДОМЛЕНИЯ КЛИЕНТУ
            if old_order and old_order.get('status') != new_status:
                self.send_status_notification(order_id, new_status, old_order.get('status'), cancel_reason)
            
            if self.current_tab == "dashboard":
                self.update_orders_table()
            elif self.current_tab == "orders":
                self.update_orders_management()
            
            self.update_stats()
            return True
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить заказ: {e}")
            return False
    
    def show_order_details(self, order_id):
        """Показать детали заказа"""
        order = next((o for o in self.orders if o.get('order_id') == order_id), None)
        if not order:
            messagebox.showerror("Ошибка", "Заказ не найден!")
            return
        
        details_window = ctk.CTkToplevel(self.root)
        details_window.title(f"Детали заказа #{order_id}")
        details_window.geometry("600x500")
        details_window.transient(self.root)
        details_window.configure(fg_color=self.colors["card_bg"])
        
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 300
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
        details_window.geometry(f"+{x}+{y}")
        
        scroll_frame = ctk.CTkScrollableFrame(details_window, fg_color=self.colors["card_bg"])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        ctk.CTkLabel(
            scroll_frame,
            text=f"📋 Заказ #{order_id}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(pady=10)
        
        # Информация о клиенте
        info_frame = ctk.CTkFrame(scroll_frame, fg_color=self.colors["primary"], corner_radius=10)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="👤 Информация о клиенте:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(anchor="w", padx=15, pady=10)
        
        info_text = f"ФИО: {order.get('user_name', 'Не указано')}\n"
        info_text += f"Телефон: {order.get('phone', 'Не указан')}\n"
        info_text += f"Адрес: {order.get('address', 'Не указан')}\n"
        info_text += f"Время заказа: {order.get('timestamp', 'Не указано')}\n"
        info_text += f"Статус: {order.get('status', 'Не указан')}"
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_light"],
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Состав заказа
        cart_frame = ctk.CTkFrame(scroll_frame, fg_color=self.colors["primary"], corner_radius=10)
        cart_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            cart_frame,
            text="🛒 Состав заказа:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(anchor="w", padx=15, pady=10)
        
        for item in order.get('cart', []):
            item_frame = ctk.CTkFrame(cart_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=15, pady=2)
            
            item_text = f"• {item.get('name', 'Неизвестный товар')} - {item.get('quantity', 0)} шт. × {item.get('price', 0)}₽"
            ctk.CTkLabel(item_frame, text=item_text, text_color=self.colors["text_light"]).pack(anchor="w")
        
        # Итоговая сумма
        total_frame = ctk.CTkFrame(scroll_frame, fg_color=self.colors["accent_gold"], corner_radius=10)
        total_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            total_frame,
            text=f"💰 ИТОГО: {order.get('total', 0)}₽",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1A1A1A"
        ).pack(padx=15, pady=15)
    
    # === УПРАВЛЕНИЕ ЗАКАЗАМИ (ПОЛНАЯ ВЕРСИЯ) ===
    
    def show_orders(self):
        """Показать все заказы"""
        self.current_tab = "orders"
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Заголовок
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="📋 Управление заказами",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(anchor="w")
        
        # Фильтры
        filters_frame = ctk.CTkFrame(self.content_frame, fg_color=self.colors["primary"], corner_radius=10)
        filters_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            filters_frame,
            text="Фильтры:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_dark"]
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Выбор статуса
        statuses = ["Все", "Новые", "Принятые", "Ожидают оплаты", "Готовятся", "В доставке", "Завершенные", "Отмененные"]
        self.status_filter = ctk.CTkComboBox(
            filters_frame,
            values=statuses,
            width=150,
            fg_color=self.colors["card_bg"],
            button_color=self.colors["accent_blue"],
            button_hover_color=self.colors["accent_blue"]
        )
        self.status_filter.set("Все")
        self.status_filter.grid(row=0, column=1, padx=10, pady=10)
        
        # Поле поиска
        self.search_entry = ctk.CTkEntry(
            filters_frame,
            placeholder_text="Поиск по ID, имени или телефону...",
            width=300,
            fg_color=self.colors["card_bg"]
        )
        self.search_entry.grid(row=0, column=2, padx=10, pady=10)
        
        # Кнопка поиска
        ctk.CTkButton(
            filters_frame,
            text="🔍 Поиск",
            command=self.apply_filters,
            fg_color=self.colors["accent_blue"],
            hover_color=self.colors["accent_blue"]
        ).grid(row=0, column=3, padx=10, pady=10)
        
        # Кнопка сброса
        ctk.CTkButton(
            filters_frame,
            text="🔄 Сбросить",
            command=self.reset_filters,
            fg_color=self.colors["text_light"],
            hover_color=self.colors["text_light"]
        ).grid(row=0, column=4, padx=10, pady=10)
        
        # Таблица заказов
        self.orders_management_frame = ctk.CTkScrollableFrame(self.content_frame, height=500)
        self.orders_management_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.update_orders_management()
    
    def apply_filters(self):
        """Применить фильтры"""
        self.update_orders_management()
    
    def reset_filters(self):
        """Сбросить фильтры"""
        self.status_filter.set("Все")
        self.search_entry.delete(0, 'end')
        self.update_orders_management()
    
    def update_orders_management(self):
        """Обновление управления заказами"""
        if not hasattr(self, 'orders_management_frame'):
            return
        
        for widget in self.orders_management_frame.winfo_children():
            widget.destroy()
        
        # Заголовки таблицы
        headers_frame = ctk.CTkFrame(self.orders_management_frame, 
                                    fg_color=self.colors["primary_light"], 
                                    height=50)
        headers_frame.pack(fill="x", pady=(0, 10))
        headers_frame.pack_propagate(False)
        
        headers = ["ID", "Клиент", "Телефон", "Адрес", "Сумма", "Статус", "Время", "Действия"]
        widths = [80, 120, 120, 150, 100, 120, 120, 200]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_dark"],
                width=width
            )
            label.grid(row=0, column=i, padx=5, pady=15, sticky="w")
        
        # Фильтрация заказов
        filtered_orders = self.filter_orders()
        
        for row, order in enumerate(filtered_orders):
            self.create_management_order_row(order, row)
    
    def filter_orders(self):
        """Фильтрация заказов"""
        status_filter = self.status_filter.get() if hasattr(self, 'status_filter') else "Все"
        search_text = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        
        filtered = self.orders.copy()
        
        # Фильтр по статусу
        if status_filter != "Все":
            status_map = {
                "Новые": "новый",
                "Принятые": "принят",
                "Ожидают оплаты": "ожидает оплаты",
                "Готовятся": "готовится",
                "В доставке": "в доставке",
                "Завершенные": "завершен",
                "Отмененные": "отменен"
            }
            if status_filter in status_map:
                filtered = [o for o in filtered if o.get('status') == status_map[status_filter]]
        
        # Фильтр по поиску
        if search_text:
            search_lower = search_text.lower()
            filtered = [o for o in filtered if 
                       search_lower in str(o.get('order_id', '')).lower() or
                       search_lower in str(o.get('user_name', '')).lower() or
                       search_lower in str(o.get('phone', '')).lower()]
        
        return sorted(filtered, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    def create_management_order_row(self, order, row):
        """Создание строки заказа для управления"""
        row_frame = ctk.CTkFrame(self.orders_management_frame, 
                                fg_color=self.colors["card_bg"], 
                                height=60)
        row_frame.pack(fill="x", pady=5)
        row_frame.pack_propagate(False)
        
        # ID заказа
        ctk.CTkLabel(row_frame, 
                    text=f"#{order.get('order_id', 'N/A')}", 
                    font=ctk.CTkFont(weight="bold"), 
                    text_color=self.colors["text_dark"],
                    width=80).grid(row=0, column=0, padx=5, pady=15)
        
        # Имя клиента
        client_name = order.get('user_name', 'Не указан')
        if len(client_name) > 12:
            client_name = client_name[:12] + "..."
        ctk.CTkLabel(row_frame, 
                    text=client_name, 
                    text_color=self.colors["text_light"],
                    width=120).grid(row=0, column=1, padx=5, pady=15)
        
        # Телефон
        phone = order.get('phone', 'N/A')
        ctk.CTkLabel(row_frame, 
                    text=phone, 
                    text_color=self.colors["text_light"],
                    width=120).grid(row=0, column=2, padx=5, pady=15)
        
        # Адрес
        address = order.get('address', 'N/A')
        if len(address) > 15:
            address = address[:15] + "..."
        ctk.CTkLabel(row_frame, 
                    text=address, 
                    text_color=self.colors["text_light"],
                    width=150).grid(row=0, column=3, padx=5, pady=15)
        
        # Сумма
        ctk.CTkLabel(row_frame, 
                    text=f"{order.get('total', 0)}₽", 
                    font=ctk.CTkFont(weight="bold"), 
                    text_color=self.colors["success"],
                    width=100).grid(row=0, column=4, padx=5, pady=15)
        
        # Статус
        status_text = order.get('status', 'новый')
        status_color = self.get_status_color(status_text)
        status_label = ctk.CTkLabel(
            row_frame, 
            text=status_text.upper(), 
            text_color="white",
            fg_color=status_color,
            corner_radius=8,
            font=ctk.CTkFont(size=10, weight="bold"),
            width=120
        )
        status_label.grid(row=0, column=5, padx=5, pady=15)
        
        # Время
        time_str = order.get('timestamp', 'N/A')
        short_time = time_str[11:16] if len(time_str) > 16 else time_str
        ctk.CTkLabel(row_frame, 
                    text=short_time, 
                    text_color=self.colors["text_light"],
                    width=120).grid(row=0, column=6, padx=5, pady=15)
        
        # Действия
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=7, padx=5, pady=15, sticky="w")
        
        # Кнопка деталей
        ctk.CTkButton(
            action_frame, 
            text="📋", 
            width=35,
            height=35,
            fg_color=self.colors["accent_blue"],
            hover_color="#2563EB",
            command=lambda oid=order.get('order_id'): self.show_order_details(oid)
        ).pack(side="left", padx=2)
        
        # Выбор статуса
        status_var = ctk.StringVar(value=order.get('status', 'новый'))
        status_menu = ctk.CTkComboBox(
            action_frame,
            values=["новый", "принят", "ожидает оплаты", "готовится", "в доставке", "завершен", "отменен"],
            variable=status_var,
            width=120,
            height=35,
            fg_color=self.colors["card_bg"],
            button_color=self.colors["accent_purple"],
            command=lambda new_status, oid=order.get('order_id'): self.update_order_status(oid, new_status)
        )
        status_menu.pack(side="left", padx=2)
    
    # === УПРАВЛЕНИЕ ТОВАРАМИ ===
    
    def show_products(self):
        """Показать управление товарами"""
        self.current_tab = "products"
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Заголовок
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="📦 Управление товарами",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(anchor="w")
        
        # Кнопка добавления товара
        ctk.CTkButton(
            title_frame,
            text="➕ Добавить товар",
            command=self.show_add_product_dialog,
            fg_color=self.colors["success"],
            hover_color=self.colors["success"]
        ).pack(anchor="e", side="right")
        
        # Таблица товаров
        self.products_frame = ctk.CTkScrollableFrame(self.content_frame, height=500)
        self.products_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.update_products_management()
    
    def update_products_management(self):
        """Обновление управления товарами"""
        if not hasattr(self, 'products_frame'):
            return
        
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        # Заголовки таблицы
        headers_frame = ctk.CTkFrame(self.products_frame, 
                                    fg_color=self.colors["primary_light"], 
                                    height=50)
        headers_frame.pack(fill="x", pady=(0, 10))
        headers_frame.pack_propagate(False)
        
        headers = ["ID", "Название", "Описание", "Цена", "Вес", "Остаток", "Статус", "Действия"]
        widths = [60, 150, 200, 80, 80, 80, 100, 150]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_dark"],
                width=width
            )
            label.grid(row=0, column=i, padx=5, pady=15, sticky="w")
        
        for row, product in enumerate(self.products):
            self.create_product_row(product, row)
    
    def create_product_row(self, product, row):
        """Создание строки товара"""
        row_frame = ctk.CTkFrame(self.products_frame, 
                                fg_color=self.colors["card_bg"], 
                                height=60)
        row_frame.pack(fill="x", pady=5)
        row_frame.pack_propagate(False)
        
        # ID товара
        ctk.CTkLabel(row_frame, 
                    text=f"#{product.get('id', 'N/A')}", 
                    font=ctk.CTkFont(weight="bold"), 
                    text_color=self.colors["text_dark"],
                    width=60).grid(row=0, column=0, padx=5, pady=15)
        
        # Название
        name = product.get('name', 'Без названия')
        ctk.CTkLabel(row_frame, 
                    text=name, 
                    text_color=self.colors["text_light"],
                    width=150).grid(row=0, column=1, padx=5, pady=15)
        
        # Описание
        description = product.get('description', '')
        if len(description) > 25:
            description = description[:25] + "..."
        ctk.CTkLabel(row_frame, 
                    text=description, 
                    text_color=self.colors["text_light"],
                    width=200).grid(row=0, column=2, padx=5, pady=15)
        
        # Цена
        ctk.CTkLabel(row_frame, 
                    text=f"{product.get('price', 0)}₽", 
                    font=ctk.CTkFont(weight="bold"), 
                    text_color=self.colors["success"],
                    width=80).grid(row=0, column=3, padx=5, pady=15)
        
        # Вес
        ctk.CTkLabel(row_frame, 
                    text=product.get('weight', 'N/A'), 
                    text_color=self.colors["text_light"],
                    width=80).grid(row=0, column=4, padx=5, pady=15)
        
        # Остаток
        stock = product.get('stock', 0)
        stock_color = self.colors["success"] if stock > 5 else self.colors["warning"] if stock > 0 else self.colors["error"]
        ctk.CTkLabel(row_frame, 
                    text=str(stock), 
                    font=ctk.CTkFont(weight="bold"), 
                    text_color=stock_color,
                    width=80).grid(row=0, column=5, padx=5, pady=15)
        
        # Статус
        is_active = product.get('is_active', True)
        status_text = "Активен" if is_active else "Неактивен"
        status_color = self.colors["success"] if is_active else self.colors["error"]
        status_label = ctk.CTkLabel(
            row_frame, 
            text=status_text, 
            text_color="white",
            fg_color=status_color,
            corner_radius=8,
            font=ctk.CTkFont(size=10, weight="bold"),
            width=100
        )
        status_label.grid(row=0, column=6, padx=5, pady=15)
        
        # Действия
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=7, padx=5, pady=15, sticky="w")
        
        # Кнопка редактирования
        ctk.CTkButton(
            action_frame, 
            text="✏️", 
            width=35,
            height=35,
            fg_color=self.colors["accent_blue"],
            hover_color="#2563EB",
            command=lambda pid=product.get('id'): self.edit_product(pid)
        ).pack(side="left", padx=2)
        
        # Кнопка удаления
        ctk.CTkButton(
            action_frame, 
            text="🗑️", 
            width=35,
            height=35,
            fg_color=self.colors["error"],
            hover_color="#DC2626",
            command=lambda pid=product.get('id'): self.delete_product(pid)
        ).pack(side="left", padx=2)
        
        # Кнопка переключения статуса
        toggle_text = "❌" if is_active else "✅"
        toggle_color = self.colors["error"] if is_active else self.colors["success"]
        ctk.CTkButton(
            action_frame, 
            text=toggle_text, 
            width=35,
            height=35,
            fg_color=toggle_color,
            hover_color=toggle_color,
            command=lambda pid=product.get('id'): self.toggle_product_status(pid)
        ).pack(side="left", padx=2)
    
    def show_add_product_dialog(self):
        """Диалог добавления товара"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Добавить товар")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.configure(fg_color=self.colors["card_bg"])
        
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 250
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 300
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(
            dialog,
            text="➕ Добавить товар",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(pady=20)
        
        # Поля формы
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Название
        ctk.CTkLabel(form_frame, text="Название товара:", anchor="w").pack(fill="x", pady=5)
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="Например: Бородинский хлеб")
        name_entry.pack(fill="x", pady=5)
        
        # Описание
        ctk.CTkLabel(form_frame, text="Описание:", anchor="w").pack(fill="x", pady=5)
        desc_entry = ctk.CTkEntry(form_frame, placeholder_text="Описание товара")
        desc_entry.pack(fill="x", pady=5)
        
        # Цена
        ctk.CTkLabel(form_frame, text="Цена (₽):", anchor="w").pack(fill="x", pady=5)
        price_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        price_entry.pack(fill="x", pady=5)
        
        # Вес
        ctk.CTkLabel(form_frame, text="Вес:", anchor="w").pack(fill="x", pady=5)
        weight_entry = ctk.CTkEntry(form_frame, placeholder_text="500г")
        weight_entry.pack(fill="x", pady=5)
        
        # Количество
        ctk.CTkLabel(form_frame, text="Количество на складе:", anchor="w").pack(fill="x", pady=5)
        stock_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        stock_entry.pack(fill="x", pady=5)
        
        # Статус
        active_var = ctk.BooleanVar(value=True)
        active_check = ctk.CTkCheckBox(form_frame, text="Товар активен", variable=active_var)
        active_check.pack(fill="x", pady=10)
        
        def save_product():
            """Сохранение товара"""
            try:
                new_id = max([p.get('id', 0) for p in self.products], default=0) + 1
                new_product = {
                    'id': new_id,
                    'name': name_entry.get(),
                    'description': desc_entry.get(),
                    'price': int(price_entry.get()),
                    'weight': weight_entry.get(),
                    'stock': int(stock_entry.get()),
                    'is_active': active_var.get()
                }
                
                self.products.append(new_product)
                self.safe_json_save(self.products, self.products_file)
                self.load_data()
                self.update_products_management()
                dialog.destroy()
                self.show_success_message("Товар успешно добавлен!")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить товар: {e}")
        
        # Кнопки
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Сохранить",
            command=save_product,
            fg_color=self.colors["success"],
            hover_color=self.colors["success"]
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Отмена",
            command=dialog.destroy,
            fg_color=self.colors["error"],
            hover_color=self.colors["error"]
        ).pack(side="right", padx=10)
    
    def edit_product(self, product_id):
        """Редактирование товара"""
        product = next((p for p in self.products if p.get('id') == product_id), None)
        if not product:
            messagebox.showerror("Ошибка", "Товар не найден!")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Редактировать товар")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.configure(fg_color=self.colors["card_bg"])
        
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 250
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 300
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(
            dialog,
            text="✏️ Редактировать товар",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(pady=20)
        
        # Поля формы
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Название
        ctk.CTkLabel(form_frame, text="Название товара:", anchor="w").pack(fill="x", pady=5)
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="Например: Бородинский хлеб")
        name_entry.insert(0, product.get('name', ''))
        name_entry.pack(fill="x", pady=5)
        
        # Описание
        ctk.CTkLabel(form_frame, text="Описание:", anchor="w").pack(fill="x", pady=5)
        desc_entry = ctk.CTkEntry(form_frame, placeholder_text="Описание товара")
        desc_entry.insert(0, product.get('description', ''))
        desc_entry.pack(fill="x", pady=5)
        
        # Цена
        ctk.CTkLabel(form_frame, text="Цена (₽):", anchor="w").pack(fill="x", pady=5)
        price_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        price_entry.insert(0, str(product.get('price', 0)))
        price_entry.pack(fill="x", pady=5)
        
        # Вес
        ctk.CTkLabel(form_frame, text="Вес:", anchor="w").pack(fill="x", pady=5)
        weight_entry = ctk.CTkEntry(form_frame, placeholder_text="500г")
        weight_entry.insert(0, product.get('weight', ''))
        weight_entry.pack(fill="x", pady=5)
        
        # Количество
        ctk.CTkLabel(form_frame, text="Количество на складе:", anchor="w").pack(fill="x", pady=5)
        stock_entry = ctk.CTkEntry(form_frame, placeholder_text="0")
        stock_entry.insert(0, str(product.get('stock', 0)))
        stock_entry.pack(fill="x", pady=5)
        
        # Статус
        active_var = ctk.BooleanVar(value=product.get('is_active', True))
        active_check = ctk.CTkCheckBox(form_frame, text="Товар активен", variable=active_var)
        active_check.pack(fill="x", pady=10)
        
        def save_changes():
            """Сохранение изменений"""
            try:
                product['name'] = name_entry.get()
                product['description'] = desc_entry.get()
                product['price'] = int(price_entry.get())
                product['weight'] = weight_entry.get()
                product['stock'] = int(stock_entry.get())
                product['is_active'] = active_var.get()
                
                self.safe_json_save(self.products, self.products_file)
                self.load_data()
                self.update_products_management()
                dialog.destroy()
                self.show_success_message("Товар успешно обновлен!")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить товар: {e}")
        
        # Кнопки
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Сохранить",
            command=save_changes,
            fg_color=self.colors["success"],
            hover_color=self.colors["success"]
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Отмена",
            command=dialog.destroy,
            fg_color=self.colors["error"],
            hover_color=self.colors["error"]
        ).pack(side="right", padx=10)
    
    def delete_product(self, product_id):
        """Удаление товара"""
        result = messagebox.askyesno("Подтверждение", "Удалить этот товар?")
        if result:
            self.products = [p for p in self.products if p.get('id') != product_id]
            self.safe_json_save(self.products, self.products_file)
            self.load_data()
            self.update_products_management()
            self.show_success_message("Товар удален!")
    
    def toggle_product_status(self, product_id):
        """Переключение статуса товара"""
        product = next((p for p in self.products if p.get('id') == product_id), None)
        if product:
            product['is_active'] = not product.get('is_active', True)
            self.safe_json_save(self.products, self.products_file)
            self.load_data()
            self.update_products_management()
    
    # === АНАЛИТИКА ===
    
    def show_analytics(self):
        """Показать аналитику"""
        self.current_tab = "analytics"
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Заголовок
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="📈 Аналитика продаж",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(anchor="w")
        
        # Статистика
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=10)
        
        # Основная статистика
        total_revenue = sum(order.get('total', 0) for order in self.orders if order.get('status') == 'завершен')
        total_orders = len([o for o in self.orders if o.get('status') == 'завершен'])
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        analytics_stats = [
            (f"💰 Общая выручка", f"{total_revenue}₽", self.colors["success"]),
            (f"📦 Всего заказов", f"{total_orders}", self.colors["accent_blue"]),
            (f"📊 Средний чек", f"{avg_order_value:.0f}₽", self.colors["accent_purple"]),
        ]
        
        for i, (title, value, color) in enumerate(analytics_stats):
            card = ctk.CTkFrame(stats_frame, corner_radius=15, fg_color=color,
                               height=100)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            card.grid_propagate(False)
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color="white"
            ).pack(expand=True, pady=(20, 0))
            
            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).pack(expand=True, pady=(0, 20))
        
        # Графики
        charts_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # График продаж по дням
        self.create_sales_chart(charts_frame)
    
    def create_sales_chart(self, parent):
        """Создание графика продаж"""
        try:
            # Анализ данных за последние 7 дней
            dates = []
            revenues = []
            
            for i in range(7):
                date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
                dates.append(date)
                day_revenue = sum(
                    order.get('total', 0) for order in self.orders 
                    if order.get('timestamp', '').startswith(date) and order.get('status') == 'завершен'
                )
                revenues.append(day_revenue)
            
            # Создание графика
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='#2A2A2A')
            ax.bar(dates, revenues, color=self.colors["accent_blue"], alpha=0.8)
            ax.set_title('Выручка за последние 7 дней', color='white', pad=20)
            ax.set_ylabel('Выручка (₽)', color='white')
            ax.set_xlabel('Дата', color='white')
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.3)
            
            # Вращение подписей дат
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            fig.tight_layout()
            
            # Встраивание в Tkinter
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            ctk.CTkLabel(
                parent,
                text=f"Ошибка построения графика: {e}",
                text_color=self.colors["error"]
            ).pack()
    
    # === НАСТРОЙКИ ===
    
    def show_settings(self):
        """Показать настройки"""
        self.current_tab = "settings"
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Заголовок
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="⚙️ Настройки системы",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(anchor="w")
        
        # Настройки уведомлений
        notif_frame = ctk.CTkFrame(self.content_frame, fg_color=self.colors["primary"], corner_radius=10)
        notif_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            notif_frame,
            text="🔔 Настройки уведомлений",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_dark"]
        ).pack(anchor="w", padx=15, pady=10)
        
        # Звуковые уведомления
        sound_var = ctk.BooleanVar(value=self.settings.get('sound_notifications', True))
        sound_check = ctk.CTkCheckBox(
            notif_frame, 
            text="Звуковые уведомления о новых заказах",
            variable=sound_var,
            command=lambda: self.update_setting('sound_notifications', sound_var.get())
        )
        sound_check.pack(anchor="w", padx=15, pady=5)
        
        # Автообновление
        auto_var = ctk.BooleanVar(value=self.settings.get('auto_refresh', True))
        auto_check = ctk.CTkCheckBox(
            notif_frame, 
            text="Автообновление данных",
            variable=auto_var,
            command=lambda: self.update_setting('auto_refresh', auto_var.get())
        )
        auto_check.pack(anchor="w", padx=15, pady=5)
        
        # Интервал обновления
        ctk.CTkLabel(notif_frame, text="Интервал обновления (секунды):", anchor="w").pack(fill="x", padx=15, pady=5)
        interval_var = ctk.StringVar(value=str(self.settings.get('refresh_interval', 3)))
        interval_slider = ctk.CTkSlider(
            notif_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            variable=interval_var,
            command=lambda v: self.update_setting('refresh_interval', int(float(v)))
        )
        interval_slider.set(self.settings.get('refresh_interval', 3))
        interval_slider.pack(fill="x", padx=15, pady=5)
        
        # Кнопки управления
        control_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        control_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            control_frame,
            text="🔄 Обновить данные",
            command=self.load_data,
            fg_color=self.colors["accent_blue"],
            hover_color=self.colors["accent_blue"]
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            control_frame,
            text="💾 Сохранить настройки",
            command=self.save_settings,
            fg_color=self.colors["success"],
            hover_color=self.colors["success"]
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            control_frame,
            text="🗑️ Очистить историю",
            command=self.clear_history,
            fg_color=self.colors["error"],
            hover_color=self.colors["error"]
        ).pack(side="right", padx=10)
    
    def update_setting(self, key, value):
        """Обновление настройки"""
        self.settings[key] = value
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            self.safe_json_save(self.settings, self.settings_file)
            self.update_interval = self.settings.get('refresh_interval', 3)
            self.show_success_message("Настройки сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def clear_history(self):
        """Очистка истории заказов"""
        result = messagebox.askyesno("Подтверждение", "Очистить всю историю заказов? Это действие нельзя отменить.")
        if result:
            try:
                self.orders = []
                self.safe_json_save(self.orders, self.orders_file)
                self.load_data()
                self.update_stats()
                if self.current_tab == "dashboard":
                    self.update_orders_table()
                elif self.current_tab == "orders":
                    self.update_orders_management()
                self.show_success_message("История заказов очищена!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось очистить историю: {e}")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BakeryManager()
    app.run()