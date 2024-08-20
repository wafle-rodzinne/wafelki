import functools
import requests
import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

from .user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        error = None

        username = request.form['username']
        password = request.form['password']

        if not username:
            error = 'Masz problem z wymyśleniem nicku? Może ci pomóc? Chodź, zaraz coś razem wymyślimy :)'
        elif not password:
            error = 'Wow jesteś pierwszą osobą która nie napisała hasła. Pssst, masz tu hasło którego nikt nie ma: dupa123. Nie ma za co.'
        else:
            db = get_db()
            error = User.register(db, username, password)

        if error is None:
            error, user_id = User.login(db, username, password)
            if error is None:
                session['user_id']  = user_id
                session['username'] = username
                session['avatar_id'] = User.getAvatarId(db, user_id) 
                return redirect('/')
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if session.get('user_id') is not None:
        return redirect(url_for('profile.index'))

    if request.method == 'POST':
        error = None

        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error, user_id = User.login(db, username, password)

        if error is None:
            session['user_id']   = user_id
            session['username']  = username
            session['avatar_id'] = User.getAvatarId(db, user_id) 
            return redirect('/')

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    return redirect('/')
