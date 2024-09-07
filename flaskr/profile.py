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
    db = get_db()

    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))

    if session.get('username') is None:
        session['username'] = User.username(db, session.get('user_id'))

    session['avatar_id'] = User.getStats(db, session.get('user_id'))['avatar_id']

    if username != session.get('username'):
        return redirect(url_for('profile.user', username=session.get('username')))

    if request.method == 'POST':
        print(request.form)
        if 'profile-avatar-button' in request.form:
            return redirect(url_for('profile.avatars'))
        elif False:
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
    avatar_price = [100 for i in range(132)]
    avatar_price.append(0)
    print(avatar_price)

    db = get_db()

    if session.get('user_id') is None:
        user_id = User.id(db, username)
    else:
        user_id = session.get('user_id')

    if user_id is None:
        return redirect(url_for('auth.login'))
        

    avatar_choice = int(request.json['avatar_choice'])
    if avatar_choice > 131: 
        User.setAvatarId(db, user_id, None)
        return jsonify({'status':'changed'})

    avatar_block = 8 - int(avatar_choice / 16)
    avatar_block_id = 1 << (avatar_choice % 16)
    print(avatar_choice, "{:04b}".format(avatar_block_id))
    user_stats = User.getStats(db, user_id)

    balance = user_stats['points']

    unlocks = user_stats['unlocks']
    unlocks_blocks = unlocks.split('-')
    unlocks_block = int('0x' + unlocks_blocks[avatar_block], 0)
    print(balance)
    print(unlocks)

    if unlocks_block & avatar_block_id:
        User.setAvatarId(db, user_id, avatar_choice)
    elif balance >= avatar_price[avatar_choice]:
        unlocks = ''
        for i, block in enumerate(unlocks_blocks):
            block = int('0x' + block, 0)
            if i == avatar_block:
                block |= avatar_block_id
            unlocks += ("{:04x}".format(block)).replace('0x', '') + '-'
        unlocks = unlocks[:-1]
        # TODO verify unlocks here and set
        print(unlocks)
        #User.setUnlocks(db, user_id, unlocks)
        #User.setAvatarId(db, user_id, avatar_choice)
    else:
        flash('Brak monetek dobija?') # TODO better msg

    # TODO Create response data
    response_data = {'test':'test'}

    return jsonify(response_data)