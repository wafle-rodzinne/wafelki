import functools
import requests
from threading import Thread

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db


from .streamer import Streamer
from .game import game

bp = Blueprint('alfabet', __name__, url_prefix='/alfabet')


@bp.route('/', methods=('GET', 'POST'))
def index():
    session.clear()

    if request.method == 'POST':
        error = None # to mogla by być lista

        username = request.form['username']

        if not username:
            error = 'Missing username. '
            flash('Musisz wpisać nazwę kanału. Dzięki :D')
        
        streamer = Streamer(username)
        db = get_db()

        id_good         = streamer.requestId()
        chatstats_good  = streamer.requestChatStats()
        db_errors       = streamer.dbInsert(db)
        avatar_good     = streamer.requestAvatar()
        
        if not id_good and username:
            error = 'Missing username id. '
            flash('Fajnie jakby taki kanał chociaż istniał...')
        elif not chatstats_good and username:
            error = 'Missing stats. '
            flash('Streamelements zawiódł... Spróbuj za chwilę może odpowie.')
        elif db_errors and username:
            error = 'Database insert error.'
            flash('Wystąpił problem z ładowaniem bazy danych, spróbuj ponownie.')
            flash('Jeśli problem się powtarza, odpuść. Może kiedyś naprawię.')

        if error is None:
            session['streamer_name'] = streamer.name
            session['streamer_avatar'] = streamer.avatar
            session['points_name'] = streamer.requestPointsName()
            streamer = None

            return redirect(url_for("alfabet.test", streamer_name=session['streamer_name']))

    return render_template('alfabet/index.html')


@bp.route('/<string:streamer_name>', methods=('GET', 'POST'))
def test(streamer_name):

    if not 'streamer_name' in session:
        flash('Ups... Coś poszło nie tak jak miało pójść. Spróbuj od początku.')
        return redirect(url_for("alfabet.index"))

    mode = 'alfabet/mode.html'
    from string import ascii_uppercase
    alphabet = ascii_uppercase
    session['alphabet'] = alphabet
    session['alpha']    = alphabet[:13]
    session['bet']      = alphabet[13:]

    if session['streamer_avatar'] == url_for('static', filename='img/missing_avatar.png'):
        flash('Będzie brakować avataru...')
        flash('Spróbuj ponownie wybrać kanał może pomoże.')
    

    if request.method == 'POST':
        error = None


        if error is None:
            mode = 'alfabet/game.html'

            if 'messages' in request.form:
                session['mode'] = 'messages'
            elif 'watchtime' in request.form:
                session['mode'] = 'watchtime'
            elif 'points' in request.form:
                session['mode'] = 'points'
            elif 'mixed' in request.form:
                session['mode'] = 'mixed'
            else:
                answers = []
                for letter in alphabet:
                    usr = request.form[f'{letter}-usr']
                    answers.append(usr)
                    if usr:
                        session[f'{letter}-usr'] = usr
                    else:
                        session[f'{letter}-usr'] = '🤡'

                db = get_db()
                max_points = 26
                results, top1, max_points = game(db, streamer_name, answers, session['mode'])
                
                session['result'] = 0
                session['max_points'] = max_points
                
                for letter in alphabet:
                    session[f'{letter}-info'] = results[letter.lower()]
                    session[f'{letter}-topu'] = top1[letter.lower()][0]
                    topv = top1[letter.lower()][1]

                    if session['mode'] == 'watchtime': 
                        hours = topv / 60.0
                        days  = hours / 24.0
                        if days >= 1.0:
                            topv = f'{round(days)} dni i {round(hours % 24)} godzin.'

                    session[f'{letter}-topv'] = f'{topv}'

                    if results[letter.lower()] == 'exact':
                        session['result'] += 1.0
                    elif results[letter.lower()] == 'close':
                        session['result'] += 0.5


                return redirect(url_for("alfabet.result", streamer_name=streamer_name))
        else:
            flash(error)

    return render_template(mode)


@bp.route('/<string:streamer_name>/wynik', methods=('GET', 'POST'))
def result(streamer_name):
    if not 'streamer_name' in session:
        flash('Ups... Coś poszło nie tak jak miało pójść. Spróbuj od początku.')
        return redirect(url_for("alfabet.index"))
    # SKOŃCZYĆ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    session['exact']     = 'Faktycznie to '
    session['close']     = 'Niestety nie jest to najlepsza odpowiedź, ale było blisko. \
                            Mam nadzieję, że ' 
    session['unknown']    = 'Albo nie umiesz pisać, albo masz za sobą 24h streama, \
                            bo to nie przypomina żadnego nicku z twojego czatu, w top 100. \
                            Jak już dojdziesz do siebie to może przypomnisz sobie\
                             o takiej osobie jak '
    session['far']       = 'Jeśli to ktoś z topki donatorów, to zachęć tę osobę \
                            do trochę większego zaangażowania. Dla twojej wiadomości, '
    session['noanswer']  = 'W jakiś sposób szanuję to, że nawet nie udajesz, \
                            że masz widzów w dupie. Szkoda tylko, że '
    session['nouser']    = 'Musisz zachęcić więcej widzów na tę literę, bo okazuje się, \
                            że nie ma ani jednego w top 100.'

    if request.method == 'POST':
        error = None

        if error is None:
            session.clear()
            return redirect(url_for("alfabet.index"))

        flash(error)

    return render_template('alfabet/result.html')


@bp.route('/info', methods=('GET', 'POST'))
def info():
    if request.method == 'POST':
        return redirect(url_for('alfabet.index'))
    return render_template('alfabet/info.html')