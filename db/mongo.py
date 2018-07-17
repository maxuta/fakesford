#!/usr/bin/env python3

from pymongo import MongoClient


def connect(db_name, host='localhost', port=27017):
    client = MongoClient(host, port)
    db = client[db_name]
    return db
