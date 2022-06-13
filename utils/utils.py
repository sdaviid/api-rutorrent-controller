import hashlib
from datetime import datetime


def gen_random_md5():
    return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()