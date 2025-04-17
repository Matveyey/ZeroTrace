import flet as ft
from .chat_list import ChatList
from .chat_view import ChatView
from modules.core.messenger_core import SecureMessenger
import os
class MessengerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.drawer = None
        self.chat_list = None
        self.chat_view = None
        self.__secure_messenger = SecureMessenger()
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
        print(self.app_data_path)
        kem_pub = self.page.client_storage.get("kem_pub")
        sign_pub = self.page.client_storage.get("sign_pub")
        keys_data = self.page.client_storage.get("keys_data")
        self.__secure_messenger.load_keys(kem_pub, sign_pub, keys_data, "Managua642")

        
    def register_screen(self):
        
        self.page.add(ft.TextField(password=True, can_reveal_password=True, label="Enter Password"))
        
    def build(self):
        self.page.title = "Messenger"
        self.page.theme_mode = "dark"

        self.chat_list = ChatList(self.page, self.__secure_messenger, on_chat_select=self.load_chat)
        self.chat_view = ChatView(self.page, self.__secure_messenger, self.chat_list.chat_service)

        self.drawer = ft.NavigationDrawer(
            controls=[
                self.chat_list.build()
            ]
        )

        appbar = ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.MENU, on_click=self.toggle_drawer),
            title=ft.Text("Messenger", size=20),
            center_title=False
        )

        self.page.appbar = appbar
        self.page.drawer = self.drawer
        self.page.add(self.chat_view.build())
        self.page.update()

    def toggle_drawer(self, e):
        self.drawer.open = not self.drawer.open
        self.page.update()

    def load_chat(self, chat_id):
        self.drawer.open = False
        self.chat_view.set_chat(chat_id)
        self.page.update()