from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
import json
import os
from datetime import datetime

# Устанавливаем размер окна для эмуляции мобильного устройства
Window.size = (360, 640)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Заголовок
        title = Label(text='Простой мессенджер', font_size=24, size_hint_y=None, height=60)
        layout.add_widget(title)
        
        # Поля ввода
        self.username_input = TextInput(hint_text='Введите ваш username', 
                                       size_hint_y=None, height=50, multiline=False)
        layout.add_widget(self.username_input)
        
        # Кнопки
        login_btn = Button(text='Войти', size_hint_y=None, height=50, 
                          background_color=(0.3, 0.7, 0.3, 1))
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        
        register_btn = Button(text='Регистрация', size_hint_y=None, height=50,
                             background_color=(0.2, 0.6, 0.9, 1))
        register_btn.bind(on_press=self.show_register_popup)
        layout.add_widget(register_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username_input.text.strip()
        if not username:
            self.show_popup('Ошибка', 'Введите username!')
            return
        
        app = App.get_running_app()
        if username in app.users:
            app.current_user = username
            app.root.current = 'main'
            self.username_input.text = ''
        else:
            self.show_popup('Ошибка', 'Пользователь не найден!')
    
    def show_register_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        
        name_input = TextInput(hint_text='Введите имя', size_hint_y=None, height=40)
        username_input = TextInput(hint_text='Введите username', size_hint_y=None, height=40)
        
        content.add_widget(name_input)
        content.add_widget(username_input)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        
        def register(btn):
            name = name_input.text.strip()
            username = username_input.text.strip()
            
            if not name or not username:
                self.show_popup('Ошибка', 'Заполните все поля!')
                return
            
            app = App.get_running_app()
            if username in app.users:
                self.show_popup('Ошибка', 'Username уже существует!')
                return
            
            app.users[username] = {"name": name, "username": username}
            app.save_data()
            popup.dismiss()
            self.show_popup('Успех', f'Пользователь {username} зарегистрирован!')
        
        register_btn = Button(text='Зарегистрироваться')
        register_btn.bind(on_press=register)
        cancel_btn = Button(text='Отмена')
        
        btn_layout.add_widget(register_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Регистрация', content=content, size_hint=(0.9, 0.6))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        
        close_btn = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self.current_chat_user = None
        
        main_layout = BoxLayout(orientation='vertical')
        
        # Верхняя панель
        top_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, 
                             spacing=10, padding=10)
        top_panel.canvas.before.clear()
        
        self.profile_label = Label(text='Профиль: ', font_size=14)
        logout_btn = Button(text='Выйти', size_hint_x=None, width=80,
                           background_color=(0.9, 0.3, 0.3, 1))
        logout_btn.bind(on_press=self.logout)
        
        top_panel.add_widget(self.profile_label)
        top_panel.add_widget(logout_btn)
        main_layout.add_widget(top_panel)
        
        # Основной контент
        content_layout = BoxLayout(orientation='horizontal')
        
        # Левая панель - поиск и чаты
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=5, padding=5)
        
        # Поиск
        search_label = Label(text='Найти:', size_hint_y=None, height=30, font_size=12)
        left_panel.add_widget(search_label)
        
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.search_input = TextInput(hint_text='Username', multiline=False)
        search_btn = Button(text='🔍', size_hint_x=None, width=40)
        search_btn.bind(on_press=self.search_user)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        left_panel.add_widget(search_layout)
        
        # Список чатов
        chats_label = Label(text='Чаты:', size_hint_y=None, height=30, font_size=12)
        left_panel.add_widget(chats_label)
        
        self.chats_layout = GridLayout(cols=1, spacing=2, size_hint_y=None)
        self.chats_layout.bind(minimum_height=self.chats_layout.setter('height'))
        
        chats_scroll = ScrollView()
        chats_scroll.add_widget(self.chats_layout)
        left_panel.add_widget(chats_scroll)
        
        content_layout.add_widget(left_panel)
        
        # Правая панель - чат
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.6, spacing=5, padding=5)
        
        # Область сообщений
        self.messages_layout = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=5)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        
        messages_scroll = ScrollView()
        messages_scroll.add_widget(self.messages_layout)
        right_panel.add_widget(messages_scroll)
        
        # Панель отправки
        send_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.message_input = TextInput(hint_text='Сообщение...', multiline=False, disabled=True)
        send_btn = Button(text='▶', size_hint_x=None, width=50, disabled=True)
        
        self.message_input.bind(on_text_validate=self.send_message)
        send_btn.bind(on_press=self.send_message)
        
        self.send_btn = send_btn  # Сохраняем ссылку для управления
        
        send_layout.add_widget(self.message_input)
        send_layout.add_widget(send_btn)
        right_panel.add_widget(send_layout)
        
        content_layout.add_widget(right_panel)
        main_layout.add_widget(content_layout)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        app = App.get_running_app()
        if app.current_user:
            user_info = app.users[app.current_user]
            self.profile_label.text = f"{user_info['name']} (@{user_info['username']})"
            self.update_chats_list()
    
    def logout(self, instance):
        app = App.get_running_app()
        app.current_user = None
        self.current_chat_user = None
        app.root.current = 'login'
    
    def search_user(self, instance):
        search_term = self.search_input.text.strip()
        if not search_term:
            return
        
        app = App.get_running_app()
        if search_term in app.users and search_term != app.current_user:
            self.start_chat_with_user(search_term)
            self.search_input.text = ''
        else:
            self.show_popup('Поиск', 'Пользователь не найден!')
    
    def start_chat_with_user(self, username):
        self.current_chat_user = username
        self.message_input.disabled = False
        self.send_btn.disabled = False
        self.update_chats_list()
        self.load_messages()
    
    def update_chats_list(self):
        self.chats_layout.clear_widgets()
        
        app = App.get_running_app()
        chat_users = set()
        
        for chat_id in app.messages:
            users = chat_id.split("_")
            if app.current_user in users:
                other_user = users[0] if users[1] == app.current_user else users[1]
                chat_users.add(other_user)
        
        for user in sorted(chat_users):
            if user in app.users:
                name = app.users[user]['name']
                btn = Button(text=f"{name}\n@{user}", size_hint_y=None, height=60, 
                           text_size=(None, None), halign='left', font_size=11)
                btn.bind(on_press=lambda x, u=user: self.select_chat(u))
                self.chats_layout.add_widget(btn)
    
    def select_chat(self, username):
        self.current_chat_user = username
        self.message_input.disabled = False
        self.send_btn.disabled = False
        self.load_messages()
    
    def load_messages(self):
        self.messages_layout.clear_widgets()
        
        if not self.current_chat_user:
            return
        
        app = App.get_running_app()
        chat_id = self.get_chat_id(app.current_user, self.current_chat_user)
        
        if chat_id in app.messages:
            for msg in app.messages[chat_id]:
                sender_name = app.users[msg['sender']]['name']
                is_me = msg['sender'] == app.current_user
                
                msg_text = f"[{msg['time']}] {sender_name}:\n{msg['message']}"
                
                msg_label = Label(text=msg_text, text_size=(None, None), 
                                size_hint_y=None, font_size=11, markup=True)
                msg_label.bind(texture_size=msg_label.setter('size'))
                
                # Разные цвета для своих и чужих сообщений
                if is_me:
                    msg_label.canvas.before.clear()
                else:
                    msg_label.canvas.before.clear()
                
                self.messages_layout.add_widget(msg_label)
        
        # Прокручиваем вниз
        Clock.schedule_once(lambda dt: setattr(self.messages_layout.parent, 'scroll_y', 0), 0.1)
    
    def get_chat_id(self, user1, user2):
        return "_".join(sorted([user1, user2]))
    
    def send_message(self, instance):
        if not self.current_chat_user or not self.message_input.text.strip():
            return
        
        app = App.get_running_app()
        chat_id = self.get_chat_id(app.current_user, self.current_chat_user)
        
        if chat_id not in app.messages:
            app.messages[chat_id] = []
        
        new_message = {
            "sender": app.current_user,
            "message": self.message_input.text.strip(),
            "time": datetime.now().strftime("%H:%M")
        }
        
        app.messages[chat_id].append(new_message)
        app.save_data()
        
        self.message_input.text = ''
        self.update_chats_list()
        self.load_messages()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        
        close_btn = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

class MessengerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.users_file = "users.json"
        self.messages_file = "messages.json"
        self.current_user = None
        self.load_data()
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(MainScreen())
        return sm
    
    def load_data(self):
        # Загружаем пользователей
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
        else:
            self.users = {}
        
        # Загружаем сообщения
        if os.path.exists(self.messages_file):
            try:
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
            except:
                self.messages = {}
        else:
            self.messages = {}
    
    def save_data(self):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

if __name__ == '__main__':
    MessengerApp().run()