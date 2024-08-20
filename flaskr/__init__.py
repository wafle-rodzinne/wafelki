import os

from flask import (Flask, redirect, url_for, render_template, current_app)

from .streamer import Streamer, SvnEmote

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/')
    def siema():
        return render_template('index.html')

    

    from . import alfabet
    app.register_blueprint(alfabet.bp)

    from . import emotomat
    app.register_blueprint(emotomat.bp)
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import profile
    app.register_blueprint(profile.bp)
    
    from . import db
    db.init_app(app)

    return app