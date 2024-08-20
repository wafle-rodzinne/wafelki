import functools
import requests
import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, 
    jsonify, after_this_request
)

from flaskr.db import get_db

from .streamer import Streamer, SvnEmote
from .session import sessionClear
from .user import User

bp = Blueprint('emotomat', __name__, url_prefix='/emotomat')


@bp.route('/', methods=('GET', 'POST'))
def index():
    sessionClear()
    streamer = None

    if session.get('user_id'):
        db = get_db()
        session['svnid'] = User.getStats(db, session.get('user_id'))['streamer_svnid']

    if request.method == 'POST':
        error = None 

        user_svnid = request.form['emotomat-id']

        if not user_svnid:
            user_svnid = None
            error = 'Missing id.'
            flash('Musisz wpisać ID. Dzięki :D')
        else:
            session['svnid'] = user_svnid

        streamer = Streamer(svnid=user_svnid)
        error = streamer.request7tvData()
            
        if error is None:
            emotes_ids = streamer.getSvnEmotesIds()
            if len(emotes_ids) < 3:
                error = 'Not enough emotes.'
                flash('Na kanale muszą być dodane przynajmniej 3 emotki.')
            else:
                session['svnEmoteCount'] = len(emotes_ids)
                # db insert emotes

        if error is None:  
            return redirect(url_for("emotomat.game"))

    return render_template('emotomat/index.html')


@bp.route('/bandyta', methods=('GET', 'POST'))
def game():
    if not 'svnid' in session:
        return redirect(url_for("emotomat.index"))

    # Refresh emote set
    streamer = Streamer(svnid=session.get('svnid'))
    error = streamer.request7tvData()
    emotes_ids = streamer.getSvnEmotesIds()

    random_emote = random.randrange(0, session['svnEmoteCount'], 1)
    for i in range(random_emote, random_emote + 100):
        session[f'svnEmoteId-{i - random_emote}'] = emotes_ids[i % session['svnEmoteCount']]


    if session.get('user_id') is None:
        session['points'] = 10000
    else:
        db = get_db()
        session['points'] = User.getPoints(db, session.get('user_id'))

    if request.method == 'POST':
        error = None 

        if error is None:
            pass
            
        return redirect(url_for("emotomat.index"))

    return render_template('emotomat/game.html', bet=bet)

@bp.route('/bandyta/bet', methods=('GET', 'POST'))
def bet():
    if session.get('user_id') is not None:
        db = get_db()
        points = User.getPoints(db, session.get('user_id'))
    else:
        points = session.get('points')

    if request.json['bet_value'] > points:
        response_data = {
        'winning_emote_id': [0,0,0],
        'points': points,
        'jackpot': False,
        'megajackpot': False,
        'bet_error': 'Not enough points',
        }
        return jsonify(response_data)


    winning_emotes = [random.randrange(0,99,1), 0, 0]

    if random.random() < 0.30:
        winning_emotes[1] = winning_emotes[0]
    else:
        winning_emotes[1] = (winning_emotes[0] + random.randrange(0, 98 ,1)) % 100

    if random.random() < 0.25:
        winning_emotes[2] = winning_emotes[1]
    else:
        winning_emotes[2] = (winning_emotes[1] + random.randrange(0, 98 ,1)) % 100

    
    if winning_emotes[0] == winning_emotes[1] and winning_emotes[1] == winning_emotes[2]:
        points_diff  = 11 * request.json['bet_value']
        jackpot = True
    else:
        points_diff = -1 * request.json['bet_value']
        jackpot = False

    db = get_db()

    if session.get('user_id') is not None:
        points = User.getPoints(db, session.get('user_id')) + points_diff
        User.setPoints(db, session.get('user_id'), points)

        won_points, lost_points = User.getWonLostPoints(db, session.get('user_id'))
        if points_diff < 0:
            lost_points += request.json['bet_value']
        else:
            won_points += 10 * request.json['bet_value']
        User.setWonLostPoints(db, session.get('user_id'), won_points, lost_points)
    else:
        session['points'] = session.get('points') + points_diff
        points = session['points']


    response_data = {
        'winning_emote_id': winning_emotes,
        'points': points,
        'jackpot': jackpot,
        'megajackpot': False,
        'bet_error': 'None',
    }

    return jsonify(response_data)

@bp.route('/points', methods=('GET', 'POST'))
def points():
    pass


def getSortedUsers():
    pass