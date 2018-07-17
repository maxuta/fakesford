#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import hmac
import json
import os

import functools

from common.init_log import init_logging

from structs import ListOf, Tutor
from common.cache import Cache

import common.helpers as ch

from db.mongo import connect

import flask

app = flask.Flask(__name__)


def verify_sign(info, sign):
    # TODO: check ip, browser, expiration time
    return sign == ch.sign(app.secret_key, info)


def authorize(f):
    @functools.wraps(f)
    def g(*args, **kwargs):
        username = get_login()
        if not username:
            return flask.redirect('/login')

        return f(*args, **kwargs)

    return g


def get_login():
    auth = flask.request.cookies.get('auth')

    if not auth:
        return

    info, sign = json.loads(auth)
    if verify_sign(info, sign):
        return info['user']


def render_template(*args, **kwargs):
    return flask.render_template(*args, login=get_login(), **kwargs)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        info = transform_flask_form(flask.request.form)
        passwd = ch.safe_password(info['username'], info['password'])

        for tutor in app._tutors.iter():
            if tutor.username == info['username']:
                if tutor.password == passwd:
                    # set cookie
                    resp = flask.make_response(flask.redirect('/tutors'))
                    userinfo = {'user': info['username']}
                    resp.set_cookie('auth', json.dumps((userinfo, ch.sign(app.secret_key, userinfo))))
                    return resp
                else:
                    return 'wrong password', 403

        return 'unknown user', 403

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    resp = flask.make_response(flask.redirect('/'))
    resp.set_cookie('auth', '')
    return resp


@app.route('/tutors')
@authorize
def tutors():
    fields = app._tutors.public_fields()
    
    def iter_tutors():
        for i in app._tutors.iter():
            yield [getattr(i, f) for f in fields]

    return render_template('tutor_list.html', fields=fields, data=list(iter_tutors()))


def transform_flask_form(form):
    res = {}
    for k, v in form.items():
        if len(v) == 0:
            res[k] = None
        elif len(v) == 1:
            res[k] = v[0]
        else:
            res[k] = v
    return res


def register_tutor(form):
    kwargs = transform_flask_form(form)

    if not kwargs.get('username'):
        return 'you should specify username', 401

    if not kwargs.get('password'):
        return 'you should specify password', 401

    if kwargs.get('password') != kwargs.get('verify_password'):
        return 'passwords do not match', 401

    del kwargs['verify_password']

    kwargs['password'] = ch.safe_password(kwargs['username'], kwargs['password'])

    subjects = kwargs.get('subjects')
    if subjects:
        kwargs['subjects'] = [s.strip() for s in subjects.split(',') if s.strip()]
    else:
        kwargs['subjects'] = []
    app._tutors.add(**kwargs)
    return flask.redirect('/')


@app.route('/add_tutor', methods=['POST', 'GET'])
def add_tutor():
    if flask.request.method == 'POST':
        return register_tutor(flask.request.form)

    what = 'tutor'
    fields = list(app._tutors.public_fields())
    return render_template('add.html', fields=fields, what=what)


def get_args():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('-l', dest='logfile', type=str, default=None, help='path to logfile')
    parser.add_argument('-w', dest='workdir', type=str, default='workdir', help='path to workdir')
    parser.add_argument('-c', '--cfg', dest='config', default='config.json', type=str, help='path to config file')

    return parser.parse_args()


def add_some_tutors():
    app._tutors.add(name='Max', surname='Gadzh', age=77)
    app._tutors.add(name='Kolya', surname='Spiridonov', age=27, subjects=['math', 'phys'])
    print(app._tutors.dump_to_dict())


def init_structs(cache_dir):
    app._db = Cache(cache_dir)
    app._tutors = ListOf(Tutor, app._db)


def workpath(path):
    return os.path.join(app.workdir, path)


def init_auth(secret):
    app.secret_key = secret


if __name__ == '__main__':
    args = get_args()

    with open(args.config) as f:
        app.cfg = json.load(f)

    app.workdir = os.path.abspath(args.workdir)
    app.db = connect('fakesford')
    
    init_logging(args.logfile)
    init_auth(app.cfg['secret'])

    init_structs(workpath('cache'))

    app.run('::', 3322, debug=True)
