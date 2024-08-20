from flask import session

def sessionClear():
    user_id = session.get('user_id')
    username = session.get('username')
    avatar_id = session.get('avatar_id')
    session.clear()
    session['user_id'] = user_id
    session['username'] = username
    session['avatar_id'] = avatar_id