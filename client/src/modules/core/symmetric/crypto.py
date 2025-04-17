from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from typing import Tuple
import os

class SymmetricCrypto:
    @staticmethod
    def encrypt(data: bytes, key: str) -> Tuple[str, str]:
        """
        Шифрование AES-256-GCM
        Возвращает (ciphertext, nonce, auth_tag)
        """
        aes = AESGCM(bytes.fromhex(key))
        nonce = os.urandom(12)
        ciphertext = aes.encrypt(nonce, data, None)
        return ciphertext.hex(), nonce.hex()

    @staticmethod
    def decrypt(ciphertext: str, key: str, nonce: str) -> str:
        """
        Дешифрование с проверкой подлинности
        """
        aes = AESGCM(bytes.fromhex(key))
        try:
            return aes.decrypt(bytes.fromhex(nonce), bytes.fromhex(ciphertext), None).hex()
        except InvalidTag:
            raise ValueError("Ошибка аутентификации данных")

