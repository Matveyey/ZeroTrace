from typing import Tuple, List
from hashlib import sha256
import json
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hmac, hashes

from .symmetric.crypto import SymmetricCrypto
from .post_quantum.crypto import PostQuantumCrypto
from .post_quantum.sign import PostQuantumSignature
from .utils import CryptoUtils, MessageType
from .api import API



from tqdm import tqdm

class SecureMessenger:
    __kem_public_key: str
    __kem_private_key: str
    __signature_public_key: str
    __signature_private_key: str
    
    
    def __init__(self):
        
        self.__quantum = PostQuantumCrypto()
        self.__symmetric = SymmetricCrypto()
        self.__api = API()
        self.__signature = PostQuantumSignature()

    def register(self, username: str, password: str) -> Tuple[str, str, dict]:
        kem_private_key, kem_public_key, signature_private_key, signature_public_key = (
            self.__quantum.generate_key_pair()
        )
    
        if self.__api.register(username, kem_public_key, signature_public_key):
    
            salt = os.urandom(16)
            aes_key = CryptoUtils.derive_key_scrypt(password, salt)
            aesgcm = AESGCM(aes_key)
            nonce = os.urandom(12)
    
            keys = {
                "kem.private": kem_private_key,
                "sig.private": signature_private_key,
            }
            encrypted_keys = {}
            for name, value in keys.items():
                ciphertext = aesgcm.encrypt(nonce, value.encode(), None)
                encrypted_keys[name] = base64.b64encode(ciphertext).decode()
    
            # HMAC для быстрой проверки пароля
            h = hmac.HMAC(aes_key, hashes.SHA256())
            h.update(b"keycheck")
            keycheck = base64.b64encode(h.finalize()).decode()
    
            data = {
                "salt": base64.b64encode(salt).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "encrypted_keys": encrypted_keys,
                "keycheck": keycheck
            }
    
    
            self.__kem_public_key = kem_public_key
            self.__kem_private_key = kem_private_key
            self.__signature_private_key = signature_private_key
            self.__signature_public_key = signature_public_key
            return kem_public_key, signature_public_key, data
        else:
            return None

    def load_keys(self, kem_public:str, sign_public:str ,data: dict, password: str) -> bool:
        salt = base64.b64decode(data["salt"])
        nonce = base64.b64decode(data["nonce"])
        encrypted_keys = data["encrypted_keys"]
        keycheck_saved = base64.b64decode(data["keycheck"])
        aes_key = CryptoUtils.derive_key_scrypt(password, salt)
        # Проверка HMAC — быстрая проверка пароля
        h = hmac.HMAC(aes_key, hashes.SHA256())
        h.update(b"keycheck")
        try:
            h.verify(keycheck_saved)
        except Exception:
            print("Wrong Password")
            return False
    
        aesgcm = AESGCM(aes_key)
    
        kem_private_key = aesgcm.decrypt(nonce, base64.b64decode(encrypted_keys["kem.private"]), None).decode()
        signature_private_key = aesgcm.decrypt(nonce, base64.b64decode(encrypted_keys["sig.private"]), None).decode()

    
        self.__kem_public_key = kem_public
        self.__kem_private_key = kem_private_key
        self.__signature_public_key = sign_public
        self.__signature_private_key = signature_private_key
        return True

    def generate_dialog_id(self,key1: str, key2: str) -> str:
        sorted_keys = sorted([key1, key2])
        key_string = "|".join(sorted_keys)
        return sha256(key_string.encode()).hexdigest()
    
    def send_message(
        self,
        recipient_public_key: str,
        message: bytes,
        msg_type: int
    ) -> bool:
        # Шаг 1: Создание общего секрета

        shared_secret, shared_secret_kem_ciphertext = self.__quantum.encapsulate(recipient_public_key)

        # Шаг 2: Шифрование сообщения
        msg_ciphertext, msg_nonce = self.__symmetric.encrypt(
            message, CryptoUtils.derive_key_hkdf(shared_secret)
        )
        # Шаг 3: Шифрование общего секрета приватным ключом отправителя
        shared_secret_aes_ciphertext, shared_secret_nonce = self.__symmetric.encrypt(
            bytes.fromhex (shared_secret), CryptoUtils.derive_key_hkdf(self.__kem_private_key)
        )
        # Шаг 4: Подписание сообщения
        signature = self.__signature.sign(message, self.__signature_private_key)

        return self.__api.send_message(
            self.__kem_public_key,
            recipient_public_key,
            shared_secret_aes_ciphertext,
            shared_secret_kem_ciphertext,
            msg_ciphertext,
            msg_nonce,
            shared_secret_nonce,
            signature,
            sha256(bytes.fromhex(self.__kem_public_key) + bytes.fromhex(self.__signature_public_key)).hexdigest(),
            msg_type,
            self.generate_dialog_id(self.__kem_public_key, recipient_public_key)
        )

    def receive_all_crypted_messages(
        self,
        time_limit: int,
    ) -> list[str]:
        # Шаг 0: Получение сообщений
        return self.__api.get_messages(self.__kem_public_key, time_limit)
    
    def decrypt_message(self,messages: List[dict]) -> List[dict]:
        decrypted_msgs = []
        for msg in tqdm(messages):
            # Шаг 1: Восстановление общего секрета
            if msg["recipient_public_key"] == self.__kem_public_key:
                shared_secret = self.__quantum.decapsulate(
                    self.__kem_private_key, msg["shared_secret_kem_ciphertext"]
                )
            else:
                shared_secret = self.__symmetric.decrypt(
                    msg["shared_secret_aes_ciphertext"],
                    CryptoUtils.derive_key_hkdf(self.__kem_private_key),
                    msg["shared_secret_aes_nonce"],
                )

            # Шаг 2: Дешифровка сообщения
            data = bytes.fromhex(self.__symmetric.decrypt(
                msg["ciphertext"],
                CryptoUtils.derive_key_hkdf(shared_secret),
                msg["nonce"],
            ))
            # Шаг 3: Проверка хеша публичных ключей
            sender = self.__api.get_user(msg["sender_public_key"])

            if (
                sha256( bytes.fromhex(msg["sender_public_key"]) + bytes.fromhex(sender["signature_public_key"])).hexdigest()
                != msg["hash_public"]
            ):
                print(sha256( bytes.fromhex(msg["sender_public_key"]) + bytes.fromhex(sender["signature_public_key"])).hexdigest())
                data = b"**Unverify**"

            # Шаг 4: Проверка подписи
            if not self.__signature.verify(data, msg["signature"], sender["signature_public_key"]):
                data = b"**Unverify**"

            decrypted_msgs.append(
                {
                    "sender": self.get_user(msg["sender_public_key"])["username"],
                    "data": data,
                    "msg_type":MessageType(msg["msg_type"]),
                    "hash": msg["hash_public"],
                    "timestamp": msg["timestamp"]
                }
            )
        return decrypted_msgs
    
    def get_dialogs(self) -> List[dict]:
        return self.__api.get_dialogs(self.__kem_public_key)
    
    def get_dialog_crypted_messages(self, dialog_hash: str, time_limit: float) -> List[dict]:
        return self.__api.get_dialog_messages(dialog_hash, time_limit)
    
    def get_user(self,public_key: str):
        return self.__api.get_user(public_key)
    
    def search_users(self, query:str):
        return self.__api.search_user(query)