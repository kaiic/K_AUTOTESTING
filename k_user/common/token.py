import hashlib
import time
import random


def generate_token(username):
    """
    生成token
    """
    timestamp = str(time.time())

    if username in (None, ""):
        sample = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        username = random.sample(sample, 16)
        username = "".join(username)

    token = hashlib.md5(bytes(username, encoding='utf-8'))
    token.update(bytes(timestamp, encoding='utf-8'))

    return token.hexdigest()

