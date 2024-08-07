import functools
import requests

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('emotomat', __name__, url_prefix='/emotomat')


@bp.route('/', methods=('GET', 'POST'))
def index():
    session.clear()

    if request.method == 'POST':
        error = None 


        if error is None:
            pass
            return redirect(url_for("emotomat.game"))

    return render_template('emotomat/index.html')


@bp.route('/bandyta', methods=('GET', 'POST'))
def game():

    if request.method == 'POST':
        error = None 
        session['jackpot'] = 'true'


        if error is None:
            pass
            return redirect(url_for("emotomat.index"))

    return render_template('emotomat/game.html')