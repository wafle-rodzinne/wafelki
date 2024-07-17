import functools
import requests

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

from threading import Thread

from .streamer import Streamer

bp = Blueprint('alfabet', __name__, url_prefix='/alfabet')

streamer = None

'''
class NewThreadedTask(Thread):
     def __init__(self, streamer, db):
        self.streamer = streamer
        self.db = db
        super(NewThreadedTask, self).__init__()
 
     def run(self):
        print('tip')
        self.streamer.dbInsert(get_db())
        print('top')
'''

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        error = None

        username = request.form['username']

        if not username:
            error = 'Username is required.'
        
        streamer = Streamer(username)
        
        if not streamer.requestId():
            error = 'Missing streamer id'
        if not streamer.requestChatStats():
            error = 'Missing stats'

        if error is None:
            session.clear()
            session['streamer_name'] = streamer.name
            db = get_db()
            #thread = NewThreadedTask(streamer, db)
            #thread.start()
            streamer.dbInsert(db)


            return redirect(url_for("alfabet.test", streamer_name=streamer.name))

        flash(error)

    return render_template('alfabet/index.html')


@bp.route('/<string:streamer_name>', methods=('GET', 'POST'))
def test(streamer_name):
    mode = None
    template = {
        'messages'  : '',
        'watchtime' : '',
        'points'    : '',
        'mixed'     : '',
        None        : 'alfabet/test.html'
    }
    
    if not 'streamer_name' in session:
        return redirect(url_for("alfabet.index"))

    if request.method == 'POST':
        error = None

        if not streamer:
            return redirect(url_for("alfabet.index"))
            
        

        if error is None:
            return redirect(url_for("alfabet.result"))

        flash(error)

    return render_template(template[mode])


@bp.route('/result', methods=('GET', 'POST'))
def result():
    if not 'streamer_name' in session:
        return redirect(url_for("alfabet.index"))

    if request.method == 'POST':
        error = None


        

        if error is None:
            session.clear()
            return redirect(url_for("alfabet.index"))

        flash(error)

    return render_template('alfabet/result.html')
