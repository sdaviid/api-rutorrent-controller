import base64
import bencoding
import hashlib
from datetime import datetime


def gen_random_md5():
    return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()


def b64encode(value):
    try:
        return base64.b64encode(value.encode()).decode()
    except Exception as err:
        print(f'excepcion base64encode {err}')
    return False


def hash_torrent(path):
    try:
        torrent_file = open(path, "rb")
        torrent_decode = bencoding.bdecode(torrent_file.read())
        return hashlib.sha1(bencoding.bencode(torrent_decode[b"info"])).hexdigest()
    except Exception as err:
        print(f'exception hash torrent {err}')
    return False