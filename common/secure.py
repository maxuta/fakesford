import pickle
import zlib
import logging
import hashlib
import random

from Crypto.Cipher import AES
from Crypto import Random


def zp(v):
    return zlib.compress(pickle.dumps(v))


def pz(v):
    return pickle.loads(zlib.decompress(v))


class AESCipher(object):
    def __init__(self, key):
        self._key = hashlib.sha256(key).digest()[:32]

    def encode(self, v):
        v = zp(v)
        pad = 16 - len(v) % 16
        rng = Random.new()
        iv = rng.read(AES.block_size)
        cipher = AES.new(self._key, AES.MODE_CFB, iv)

        return {
            'pad': pad,
            'iv': iv,
            'data': cipher.encrypt(v + rng.read(pad))
        }

    def decode(self, v):
        cipher = AES.new(self._key, AES.MODE_CFB, v['iv'])

        return pz(cipher.decrypt(v['data'])[:-v['pad']])


class MTCipher(object):
    def __init__(self, key):
        self._key = key

    def apply_key(self, v):
        r = random.Random(self._key)

        return str(bytearray([x ^ r.randint(0, 255) for x in bytearray(v)]))

    def encode(self, v):
        return self.apply_key(zp(v))

    def decode(self, v):
        return pz(self.apply_key(v))


ciphers = [AESCipher, MTCipher]


def encode(key, v):
    return ciphers[0](key).encode(v)


def decode(key, v):
    for c in ciphers:
        try:
            return c(key).decode(v)
        except Exception as e:
            logging.debug('can not decode message by %s: %s', str(c), e)

    raise Exception('can not decode message')
