import os
from time import time, sleep

import flet as ft

from .chat_list import ChatList
from .chat_view import ChatView
from modules.core.messenger_core import SecureMessenger
from modules.database import MessageDatabase

from .login import LoginSystem



class MessengerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.drawer = None
        self.chat_list = None
        self.chat_view = None
        self.__secure_messenger = SecureMessenger()
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        self.database = MessageDatabase(self.app_data_path)

    def update_database_messages(self):
        while True:
            sleep(5)
            last_message_time = self.page.client_storage.get("last_check")
            if not last_message_time:
                last_message_time = 0
            new_message = self.__secure_messenger.receive_all_crypted_messages(
                last_message_time
            )
            if new_message:
                for dialog in set([msg["dialog_hash"] for msg in new_message]):
                    self.database.add_message("", 0, 5, time(), dialog)
                decrypted_messages = self.__secure_messenger.decrypt_message(
                    new_message
                )
                self.database.delete_type_five_messages()
                for message in decrypted_messages:
                    print(message)
                    self.database.add_message(
                        message["sender"],
                        message["data"],
                        message["msg_type"].value,
                        message["timestamp"],
                        message["dialog_hash"],
                    )
            self.page.client_storage.set("last_check", time())
    def start(self):
        self.page.title = "ZeroTrace"
        self.page.theme_mode = "dark"
        self.login_system = LoginSystem(self.page, self.__secure_messenger, self.build)
        self.login_system.build()

    def build(self, password):
        self.page.clean()
        self.chat_list = ChatList(
            self.page, self.__secure_messenger, on_chat_select=self.load_chat
        )
        self.chat_view = ChatView(
            self.page,
            self.__secure_messenger,
            self.chat_list.chat_service,
            self.database,
        )

        self.drawer = ft.NavigationDrawer(controls=[self.chat_list.build()])

        appbar = ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.MENU, on_click=self.toggle_drawer),
            title=ft.Text("Messenger", size=20),
            center_title=False,
        )

        self.page.appbar = appbar
        self.page.drawer = self.drawer
        self.page.add(self.chat_view.build())
        self.page.run_thread(self.update_database_messages)
        self.page.run_thread(self.chat_view.update_chat_view)
        self.page.update()

    def toggle_drawer(self, e):
        self.drawer.open = not self.drawer.open
        self.page.update()

    def load_chat(self, chat_id):
        self.drawer.open = False
        self.chat_view.set_chat(chat_id)
        self.page.update()
