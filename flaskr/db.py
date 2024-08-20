import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db_channel():
    db = get_db()
    with current_app.open_resource('db/channel.sql') as f:
        db.executescript(f.read().decode('utf8'))

def init_db_user():
    db = get_db()
    with current_app.open_resource('db/user.sql') as f:
        db.executescript(f.read().decode('utf8'))

def init_db():
    init_db_channel()
    init_db_user()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_db_channel_command)
    app.cli.add_command(get_user_list_command)


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
    
# Do resetowania częsci z kanałami bez naruszania użytkowników
@click.command('init-db-channel') 
def init_db_channel_command():
    init_db_channel()
    click.echo('Initialized the channel part database.')

@click.command('get-user-list')
def get_user_list_command():
    db = get_db()
    users = db.execute(
        'SELECT * FROM user_info',
    ).fetchall()
    for user in users:
        row = ''
        for col in user:
            row += str(col) + ' '
        click.echo(row)