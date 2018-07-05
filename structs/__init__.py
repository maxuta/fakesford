#!/usr/bin/env python3

import json
import logging

from .units import Tutor, Pupil


class ListOf(object):
    def __init__(self, unit_class, db):
        self._class = unit_class
        self._db = db
        self.load()

    def gen_index(self):
        if not self._list:
            return 0

        return self._list[-1].id + 1

    def iter(self):
        return iter(self._list)

    def store_key(self):
        return self._class.__name__.lower() + 's'

    def add(self, **kwargs):
        unit = self._class(id=self.gen_index(), **kwargs)
        self._list.append(unit)
        self.store()

    def dump_to_dict(self):
        return [i.dump() for i in self._list]

    def store(self):
        self._db.store(self.store_key(), self.dump_to_dict())

    def load(self):
        self._list = []
        for i in self._db.load(self.store_key(), []):
            logging.warning('load: %s', i)
            self._list.append(self._class(**i))

    def fields(self):
        return self._class._fields
