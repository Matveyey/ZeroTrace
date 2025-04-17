
from modules.ui.models.message import Message
from modules.core.messenger_core import SecureMessenger
from modules.core.utils import MessageType

from datetime import datetime

class MessageService:
    def __init__(self, messenger: SecureMessenger):
        self.__messenger = messenger

    def get_messages(self, chat_id: str) -> list[Message]:
        messages = []
        json_messages = self.__messenger.decrypt_message(self.__messenger.get_dialog_crypted_messages(chat_id,0))
        for message in json_messages:
            if message["msg_type"] == MessageType.TEXT:
                messages.append(Message(text=message["data"].decode(), sender=message["sender"], timestamp=datetime.fromtimestamp(message["timestamp"])))
        print(messages)
        return messages

    def send_message(self, public_key: str, message: Message):
        self.__messenger.send_message(public_key,message.text.encode(),0)

    def delete_message(self, chat_id: str, message_index: int):
        pass