import flet as ft
from modules.ui.services.chat_service import ChatService

class ChatList:
    def __init__(self, page:ft.Page, messenger, on_chat_select):
        self.page = page
        self.chat_service = ChatService(messenger)
        self.on_chat_select = on_chat_select
        self.search_visible = False
        self.search_box = ft.TextField(width=200,hint_text="Search...", on_change=self.search)
    def build(self):
        self.chat_list_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.load_chats()
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[self.search_box, ft.IconButton(icon=ft.Icons.SEARCH_ROUNDED)]),
                    self.chat_list_column
                ]
            ),
            width=300,
            padding=10,
        )

    def load_chats(self, query=None):
        self.chat_list_column.controls.clear()
        chats = self.chat_service.get_chats(query)
        for dialog_hash in chats:
            self.chat_list_column.controls.append(
                ft.ListTile(
                    title=ft.Text(chats[dialog_hash]["name"]),
                    on_click=lambda e, cid=dialog_hash: self.on_chat_select(cid)
                )
            )
        self.page.update()

    def toggle_search(self, e):
        self.search_visible = not self.search_visible
        self.load_chats()

    def search(self, e):
        self.load_chats(query=self.search_box.value)
