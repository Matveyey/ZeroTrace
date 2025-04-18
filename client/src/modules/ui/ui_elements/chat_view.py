import flet as ft

from modules.core.messenger_core import SecureMessenger
from modules.ui.services.message_service import MessageService
from modules.ui.services.chat_service import ChatService
from modules.ui.models.message import TextMessage,LoadAnim


class ChatView:
    def __init__(
        self, page: ft.Page, messenger: SecureMessenger, chat_service: ChatService
    ):
        self.page = page
        self.messages_column = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.input_field = ft.TextField(hint_text="Type a message...", expand=True)
        self.send_button = ft.IconButton(icon=ft.Icons.SEND, on_click=self.send_message)
        self.message_service = MessageService(messenger)
        self.load_ring = ft.ProgressRing()
        self.__chat_service = chat_service
        self.current_chat_id = None
        self.messages = []
    def build(self):
        return ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Container(content=self.messages_column, expand=True),
                    ft.Row(controls=[self.input_field, self.send_button]),
                ],
                expand=True,
            ),
        )

    def load_messages(self, messages):
        if messages:
            for i,message in enumerate(self.messages):
                if isinstance(message, LoadAnim):
                    self.messages.pop(i)
                    self.messages_column.controls.pop(i)
            for msg in messages:
                self.messages.append(msg)
                if isinstance(msg,LoadAnim):
                    self.messages_column.controls.append(ft.ProgressRing())
                elif isinstance(msg, TextMessage):
                    self.messages_column.controls.append(ft.Text(f"{msg.sender}: {msg.text}"))
            self.page.update()

    def set_chat(self, chat_id):
        self.current_chat_id = chat_id
        self.messages_column.controls.clear()
        self.messages.clear()
        messages = self.message_service.get_messages(chat_id)
        self.load_messages(messages)

    def send_message(self, e):
        if self.input_field.value and self.current_chat_id:
            msg = TextMessage(text=self.input_field.value, sender="You")
            self.messages_column.controls.append(
                ft.Row(
                    [
                        ft.ProgressRing(scale=0.4),
                        ft.Text(f"{msg.sender}: {msg.text}"),
                    ]
                )
            )
            index_msg = len(self.messages_column.controls)
            self.input_field.value = ""
            self.page.update()
            self.message_service.send_message(
                self.__chat_service.mock_chats[self.current_chat_id]["public_key"],
                msg,
            )
            self.messages_column.controls[index_msg - 1] = ft.Text(
                f"{msg.sender}: {msg.text}"
            )
            self.page.update()
