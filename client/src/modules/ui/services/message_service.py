
from modules.ui.models.message import TextMessage
from modules.core.messenger_core import SecureMessenger

class MessageService:
    def __init__(self, messenger: SecureMessenger):
        self.__messenger = messenger

    def get_messages(self, chat_id: str) -> list[TextMessage]:
        pass

    def send_message(self, public_key: str, message: TextMessage):
        self.__messenger.send_message(public_key,message.text.encode(),0)

    def delete_message(self, chat_id: str, message_index: int):
        pass