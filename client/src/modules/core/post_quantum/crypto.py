import oqs
from typing import Tuple


class PostQuantumCrypto:
    @staticmethod
    def generate_key_pair() -> Tuple[str, str, str, str]:
        """
        Генерация ключевой пары:
        - Kyber512 (KEM)
        - Dilithium2 (Signature)
        Возвращает: (kem_private_key, kem_public_key, signature_private_key, signature_public_key)
        Все ключи представлены в hex.
        """
        with oqs.KeyEncapsulation("Kyber512") as kem, oqs.Signature("Dilithium2") as sig:
            kem_public_key = kem.generate_keypair()
            kem_private_key = kem.export_secret_key()

            sig_public_key = sig.generate_keypair()
            sig_private_key = sig.export_secret_key()

        return (
            kem_private_key.hex(),
            kem_public_key.hex(),
            sig_private_key.hex(),
            sig_public_key.hex(),
        )

    @staticmethod
    def encapsulate(public_key: str) -> Tuple[str, str]:
        """
        Инкапсуляция секрета с использованием Kyber512
        :param public_key: публичный ключ KEM (hex)
        :return: (shared_secret_hex, ciphertext_hex)
        """
        with oqs.KeyEncapsulation("Kyber512") as kem:
            ciphertext, shared_secret = kem.encap_secret(bytes.fromhex(public_key))
        return shared_secret.hex(), ciphertext.hex()

    @staticmethod
    def decapsulate(private_key: str, ciphertext: str) -> str:
        """
        Декапсуляция секрета с использованием Kyber512
        :param private_key: приватный ключ KEM (hex)
        :param ciphertext: шифртекст (hex)
        :return: shared_secret_hex
        """
        with oqs.KeyEncapsulation("Kyber512", bytes.fromhex(private_key)) as kem:
            shared_secret = kem.decap_secret(bytes.fromhex(ciphertext))
        return shared_secret.hex()