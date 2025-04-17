from oqs import Signature
from typing import Tuple

class PostQuantumSignature:
    ALGORITHM = "Dilithium2"  # Можно заменить на другой вариант SPHINCS+

    @staticmethod
    def generate_keypair() -> Tuple[str, str]:
        """
        Генерация ключевой пары SPHINCS+ с использованием pyOQS.
        Возвращает (public_key, private_key) в hex.
        """
        with Signature(PostQuantumSignature.ALGORITHM) as signer:
            public_key = signer.generate_keypair()
            secret_key = signer.export_secret_key()
            return public_key.hex(), secret_key.hex()

    @staticmethod
    def sign(message: bytes, private_key_hex: str) -> str:
        """
        Подписывает сообщение с использованием SPHINCS+.
        Возвращает подпись в hex.
        """
        private_key = bytes.fromhex(private_key_hex)
        with Signature(PostQuantumSignature.ALGORITHM, private_key) as signer:
            signature = signer.sign(message)
            return signature.hex()

    @staticmethod
    def verify(message: bytes, signature_hex: str, public_key_hex: str) -> bool:
        """
        Проверяет подпись с использованием SPHINCS+.
        """
        signature = bytes.fromhex(signature_hex)
        public_key = bytes.fromhex(public_key_hex)
        with Signature(PostQuantumSignature.ALGORITHM) as verifier:
            return verifier.verify(message, signature, public_key)




