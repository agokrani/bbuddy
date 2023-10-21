import os
from cryptography.fernet import Fernet

key = os.environ['FERNET_KEY']
cipher_suite = Fernet(key)

def encrypt(text):
    # Encrypt data
    cipher_text = cipher_suite.encrypt(text.encode())

    return cipher_text


def decrypt(cipher_text):
    text = cipher_suite.decrypt(cipher_text).decode()

    return text
