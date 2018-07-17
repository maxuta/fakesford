#!/usr/bin/env python3

import common.helpers as ch
from common.exc import AuthError, RecordNotExists
from pymongo.errors import DuplicateKeyError


class User(object):
    def __init__(self, collection, username, password, type, **kwargs):
        self._collection = collection
        self.username = username
        self.password = password
        self.type = type
        self._conf = ch.fast_copy(kwargs)

    def dump(self):
        res = {
            'username': self.username,
            'password': self.password,
            'type': self.type,
        }
        res.update(self._conf)
        return res

    def store(self):
        self._collection.update(**self.dump())


class Tutor(User):
    pass


class Pupil(User):
    pass


class UserCollection(object):
    def __init__(self, db):
        self._db = db
        self._collection = db.users

    def add(self, username, password, verify_password, type, **kwargs):
        if password != verify_password:
            raise AuthError

        rec = ch.fast_copy(kwargs)
        rec.update({'_id': username, 'password': ch.safe_password(username, password), 'type': type})

        return self._collection.insert_one(rec).inserted_id

    def update(self, username, **kwargs):
        rec = ch.fast_copy(kwargs)

        res = self._collection.update_one({'_id': username}, {'$set': rec})
        if res.matched_count != 1:
            raise RecordNotExists('user: %s' % username)

    def get(self, username):
        rec = self._collection.find_one({'_id': username})
        if not rec:
            raise RecordNotExists('user: %s' % username)

        rec['username'] = rec['_id']
        del rec['_id']

        if rec['type'] == 'tutor':
            return Tutor(collection=self, **rec)
        elif rec['type'] == 'pupil':
            return Pupil(collection=self, **rec)
        else:
            raise ValueError('user %s has unknown type (%s)' % (username, rec['type']))

    def iter_all(self):
        return self._collection.find()
