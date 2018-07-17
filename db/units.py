#!/usr/bin/env python3

import json
from collections import namedtuple
import common.helpers as ch


class BaseStruct(object):
    def dump(self):
        return {k: getattr(self, k) for k in self._fields}


_tutor_class = namedtuple('TutorBase', ['username', 'password', 'name', 'surname', 'age', 'subjects'])


class Tutor(_tutor_class, BaseStruct):
    def __new__(cls, username, password, name, surname, age=None, subjects=None):
        if subjects is None:
            subjects = []
        else:
            subjects = list(sorted(set(subjects)))

        self = super().__new__(cls, username, password, name, surname, age, subjects)

        return self


class Pupil(BaseStruct):
    def __init__(self, id, name, surname, age=None):
        self.id = id
        self.name = name
        self.surname = surname
        self.age = age
