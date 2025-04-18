from dataclasses import dataclass
from time import time


@dataclass
class TextMessage:
    text: str
    sender: str
    timestamp: float = time()
@dataclass
class LoadAnim:
    timestamp: float = time()
