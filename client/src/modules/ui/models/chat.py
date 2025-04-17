from dataclasses import dataclass


@dataclass
class Chat:
    id: str
    name: str
    last_message: str = ""
