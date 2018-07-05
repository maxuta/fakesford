import os
import zlib
import simplejson as json
import time
import pickle
import logging
import traceback

import common.helpers as h


_default_value = object()


class Cache(object):
    def __init__(self, where):
        self._where = os.path.abspath(where)

        try:
            os.makedirs(self._where)
        except OSError:
            pass

    def where(self):
        return self._where

    def key_path(self, key):
        return os.path.join(self._where, str(key))

    def get(self, key, func):
        path = self.key_path(key)

        def calc():
            if not os.path.isfile(path):
                res = func()
                if res is _default_value:
                    raise NameError("name '%s' is not defined" % key)
                self.store_direct(path, res)

            try:
                with open(path, 'rb') as f:
                    return pickle.loads(f.read())
            except Exception as e:
                os.unlink(path)
                raise e

        return calc()
        for _ in range(2):
            try:
                return calc()
            except Exception as e:
                pass

        raise e

    def store_direct(self, path, value):
        h.writefile(path, pickle.dumps(value), chmod=0o600)

    def store(self, key, value):
        path = self.key_path(key)

        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass

        self.store_direct(path, value)

    def load(self, key, value=_default_value):
        return self.get(key, lambda: value)

    def delete(self, key):
        path = self.key_path(key)
        try:
            os.unlink(path)
        except Exception as e:
            logging.error('Can\'t delete %s. Error: %s', key, e)

    def iter_dir(self, key):
        path = self.key_path(key)
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)

                if os.path.isfile(full_path):
                    item_key = os.path.join(key, item)

                    yield item_key, self.load(item_key)
        except OSError:
            raise NameError('%s is not a dir' % key)
