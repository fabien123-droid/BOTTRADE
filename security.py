import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class EncryptionManager:
    def __init__(self):
        # La clé doit faire 32 octets pour AES-256
        key = os.getenv("ENCRYPTION_KEY", "default_secret_key_32_chars_long!!")
        self.key = key.encode().ljust(32)[:32]
        self.backend = default_backend()

    def encrypt(self, text: str) -> str:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(text.encode()) + padder.finalize()
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + encrypted).decode()

    def decrypt(self, encrypted_text: str) -> str:
        data = base64.b64decode(encrypted_text)
        iv = data[:16]
        encrypted_content = data[16:]
        
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        
        decrypted_padded = decryptor.update(encrypted_content) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted.decode()
