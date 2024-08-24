import functools
import requests

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from flaskr.db import get_db

from .user import User
from .streamer import Streamer

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/', methods=('GET', 'POST'))
def index():
    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))

    if session.get('username') is None:
        db = get_db()
        session['username'] = User.username(db, session.get('user_id'))

    return redirect(url_for('profile.user', username=session.get('username')))


@bp.route('/<string:username>', methods=('GET', 'POST'))
def user(username):
    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))

    if session.get('username') is None:
        db = get_db()
        session['username'] = User.username(db, session.get('user_id'))

    if username != session.get('username'):
        return redirect(url_for('profile.user', username=session.get('username')))

    if request.method == 'POST':

        return redirect(url_for('auth.logout'))

    return render_template('profile/user.html')


@bp.route('/<string:username>/stats', methods=('GET', 'POST'))
def stats(username):
    db = get_db()

    if session.get('user_id') is None:
        user_id = User.id(db, username)
    else:
        user_id = session.get('user_id')

    if user_id is None:
        return redirect(url_for('auth.login'))
        
    response_data = User.getStats(db, user_id)
    svnid = response_data['streamer_svnid']
    response_data.update({'streamer_svn_name':Streamer.request7tvUsername(svnid)})

    return jsonify(response_data)


@bp.route('/<string:username>/svnbind', methods=['POST'])
def svnbind(username):
    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))

    db = get_db()
    svnid = request.json['svnid']

    if User.setSvnId(db, session.get('user_id'), svnid) is None:
        if svnid is None:
            flash('Pomyślnie usunięto profil 7tv', 'good')
        else:
            flash('Pomyślnie przypisano profil 7tv', 'good')
    else:
        flash('Nie udało się zaktualizować profilu 7tv.')

    #return render_template('profile/user.html')
    return jsonify({'work':'done'})
    #return redirect(url_for('profile.user', username=username))
    

@bp.route('/<string:username>/avatars', methods=('GET', 'POST'))
def avatars(username):
    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))

    if session.get('username') is None:
        db = get_db()
        session['username'] = User.username(db, session.get('user_id'))

    if username != session.get('username'):
        return redirect(url_for('profile.avatars', username=session.get('username')))
    
    if request.method == 'POST':

        return redirect('/')

    return render_template('profile/avatars.html')
    
# TODO Set or buy avatar
# if buy setUnlocks() -> setAvatarId()
# if choose setAvatarId()
@bp.route('/<string:username>/avatars/set', methods=('GET', 'POST'))
def setAvatar(username):
    db = get_db()

    if session.get('user_id') is None:
        user_id = User.id(db, username)
    else:
        user_id = session.get('user_id')

    if user_id is None:
        return redirect(url_for('auth.login'))
        
    response_data = User.getStats(db, user_id)
    svnid = response_data['streamer_svnid']
    response_data.update({'streamer_svn_name':Streamer.request7tvUsername(svnid)})

    return jsonify(response_data)