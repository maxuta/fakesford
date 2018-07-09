#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from common.init_log import init_logging

from structs import ListOf, Tutor
from common.cache import Cache

import flask

from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

from forms import LoginForm

app = flask.Flask(__name__)


def render_template(*args, **kwargs):
    return flask.render_template(*args, **kwargs)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if flask.g.user is not None and flask.g.user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        flask.session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])

    return render_template('login.html', 
            title = 'Sign In',
            form = form,
            providers = app.config['OPENID_PROVIDERS'])


@app.route('/tutors')
def tutors():
    fields = app._tutors.fields()
    
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
    subjects = kwargs.get('subjects')
    if subjects:
        kwargs['subjects'] = [s.strip() for s in subjects.split(',') if s.strip()]
    else:
        kwargs['subjects'] = []
    app._tutors.add(**kwargs)


@app.route('/add_tutor', methods=['POST', 'GET'])
def add_tutor():
    if flask.request.method == 'POST':
        register_tutor(flask.request.form)
        return flask.redirect('/')

    what = 'tutor'
    fields = list(app._tutors.fields())
    if 'id' in fields:
        fields.remove('id')

    return render_template('add.html', fields=fields, what=what)


def get_args():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('-l', dest='logfile', type=str, default=None, help='path to logfile')
    parser.add_argument('-w', dest='workdir', type=str, default='workdir', help='path to workdir')

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


def init_auth():
    lm = LoginManager()
    lm.init_app(app)
    oid = OpenID(app, workpath('tmp'))


if __name__ == '__main__':
    args = get_args()

    app.workdir = os.path.abspath(args.workdir)
    init_logging(args.logfile)

    init_structs(workpath('cache'))

    app.run('::', 3322, debug=True)
