from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import hashes
from enum import Enum

class CryptoUtils:
    @staticmethod
    def derive_key_hkdf(key: str) -> str:
        """
        Генерация ключа из общего секрета через HKDF
        """
        key_bytes = bytes.fromhex(key)
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"aes_key_derivation",
        ).derive(key_bytes).hex()
    def derive_key_scrypt(password: str, salt: bytes, length: int = 32) -> bytes:
        kdf = Scrypt(salt=salt, length=length, n=2**14, r=8, p=1)
        return kdf.derive(password.encode())

class MessageType(Enum):
    TEXT = 0
    FILE = 1
    IMG = 2
    LOAD = 5