#!/usr/bin/env python3

import json
import logging

from .units import Tutor, Pupil


class ListOf(object):
    def __init__(self, unit_class, db):
        self._class = unit_class
        self._db = db
        self.load()

    def iter(self):
        return iter(self._list)

    def store_key(self):
        return self._class.__name__.lower() + 's'

    def add(self, **kwargs):
        unit = self._class(**kwargs)
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

    def public_fields(self):
        res = []
        for f in self.fields():
            if f not in ('username', 'password'):
                res.append(f)

        return res
