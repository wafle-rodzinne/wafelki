import os

from flask import (Flask, redirect, url_for, render_template, current_app)

from .db import init_db
from .streamer import Streamer, SvnEmote
from .gdrive import GDrive

from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import datetime
import time

import re

DB_PATH          = "./instance/flaskr.sqlite"
DB_MOD_DATE      = 0
LAST_DB_MOD_DATE = 0

def gdrive_daily_db_backup():
    print(' $ Started Backup')
    for i in range(5):
        date = f'{datetime.datetime.now()}'
        date = date[:19]
        #date_formated = re.sub('[:]', '-', date)
        date_formated = re.sub('[ ]', '_', date)
        filename = date_formated + '_flaskr.sqlite'
        if GDrive.uploadDB(filename, 'DailyBackup'):
            print(' $ Backup Succesfull')
            return
    print(' ! Backup Unsuccesfull')
    return

def gdrive_db_update():
    global LAST_DB_MOD_DATE
    global DB_MOD_DATE
    global DB_PATH

    DB_MOD_DATE = time.ctime(os.path.getmtime(DB_PATH))

    if LAST_DB_MOD_DATE != DB_MOD_DATE:
        print('\n $ Started Database Update: ', str(datetime.datetime.now()))
        db_backup_rename = GDrive.renameBackupDB('flaskr_backup.sqlite', 'flaskr_backup_delete.sqlite')
        db_rename        = GDrive.renameBackupDB('flaskr.sqlite', 'flaskr_backup.sqlite')
        db_upload        = GDrive.uploadDB()
        db_delete_backup = GDrive.deleteOldBackupDB()
        if db_backup_rename and db_rename and \
           db_upload and db_delete_backup:
            LAST_DB_MOD_DATE = DB_MOD_DATE
            print('  * Database updated succesfully.')
        else:
            print("  * Database wasn't fully updated.")
        print(' $ Database Update finished: ', str(datetime.datetime.now()), '\n')

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

    if not GDrive.downloadDB():
        init_db()
        print(' ! Created clean database.')
    else:
        global DB_MOD_DATE
        global LAST_DB_MOD_DATE
        DB_MOD_DATE      = time.ctime(os.path.getmtime("./instance/flaskr.sqlite"))
        LAST_DB_MOD_DATE = DB_MOD_DATE
        print(' $ Database downloaded.')

    gdrive_scheduler = APScheduler()
    gdrive_scheduler.add_job(func=gdrive_db_update, args=[], trigger='interval', id='gdrive_db_update', seconds=60)
    gdrive_scheduler.start()

    gdrive_daily_scheduler = BackgroundScheduler()

    trigger = CronTrigger(
        year="*", month="*", day="*", hour="4", minute="0", second="0"
    )
    gdrive_daily_scheduler.add_job(
        gdrive_daily_db_backup,
        trigger=trigger,
        args=[],
        name="daily backup",
    )
    gdrive_daily_scheduler.start()

    return app
