import functools
import requests

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from flaskr.db import get_db

from .user import User

bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')

@bp.route('/', methods=('GET', 'POST'))
def leaderboard():
    db = get_db()
        
    response_data = User.getLeaderboard(db)

    return jsonify(response_data)