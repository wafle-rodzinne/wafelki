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
            print(db_errors)
            flash('Wystąpił problem z ładowaniem bazy danych, spróbuj ponownie.')
            flash('Jeśli problem się powtarza, odpuść. Może kiedyś naprawię.')

        if error is None:
            session['streamer_name'] = streamer.name
            session['streamer_avatar'] = streamer.avatar
            session['points_name'] = streamer.requestPointsName()


            return redirect(url_for("alfabet.test", streamer_name=streamer.name))

    return render_template('alfabet/index.html')


@bp.route('/<string:streamer_name>', methods=('GET', 'POST'))
def test(streamer_name):
    mode = 'alfabet/mode.html'
    from string import ascii_uppercase
    alphabet = ascii_uppercase
    session['alphabet'] = alphabet
    session['alpha']    = alphabet[:13]
    session['bet']      = alphabet[13:]

    if session['streamer_avatar'] == url_for('static', filename='img/missing_avatar.png'):
        flash('Będzie brakować avataru...')
        flash('Spróbuj ponownie wybrać kanał może pomoże.')
    
    if not 'streamer_name' in session:
        return redirect(url_for("alfabet.index"))

    if request.method == 'POST':
        error = None


        if error is None:
            mode = 'alfabet/game.html'

            if 'messages' in request.form:
                print('messages')
                session['mode'] = 'messages'
            elif 'watchtime' in request.form:
                print('watchtime')
                session['mode'] = 'watchtime'
            elif 'points' in request.form:
                print('points')
                session['mode'] = 'points'
            elif 'mixed' in request.form:
                session['mode'] = 'mixed'
            else:
                print('gamingo')
                # to mogla by byc funkcja
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
                            topv = f'{round(days)} dni i {round(hours % 24)}'

                    session[f'{letter}-topv'] = f'{topv}'

                    if results[letter.lower()] == 'exact':
                        session['result'] += 1.0
                    elif results[letter.lower()] == 'close':
                        session['result'] += 0.5
                # ughh dużo linijek kodu z góry przepraszam

                return redirect(url_for("alfabet.result"))
        else:
            flash(error)

    return render_template(mode)


@bp.route('/result', methods=('GET', 'POST'))
def result():
    if not 'streamer_name' in session:
        print("Brak streamera")
        return redirect(url_for("alfabet.index"))

    session['exact']     = '(wiadomosc za zgadniecie)'
    session['close']     = '(wiadomosc za bycie blisko)' # top 5
    session['unknown']    = 'Albo nie umiesz pisać, albo masz za sobą 24h streama, \
                            bo to nie przypomina żadnego nicku z twojego czatu, w top 100. \
                            Jak już dojdziesz do siebie to może przypomnisz sobie\
                             o takiej osobie jak ' # top < 5 and answer unknown
    session['far']       = '(wiadomosc za bycie daleko💀)' # top >= 5 and answer unknown
    session['noanswer']  = 'W jakiś sposób szanuję to, że nawet nie udajesz, \
                            że masz widzów w dupie. Szkoda tylko, że '
    session['nouser']    = '(wiadomosc za brak widza)'

    if request.method == 'POST':
        error = None

        if error is None:
            session.clear()
            return redirect(url_for("alfabet.index"))

        flash(error)

    return render_template('alfabet/result.html')
