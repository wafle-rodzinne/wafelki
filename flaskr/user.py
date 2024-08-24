from werkzeug.security import check_password_hash, generate_password_hash

from .streamer import Streamer

class User:
    #def __init__(self, name):
    #    self.name   = name
    #    self.points = 0

    def register(db, name, password):
        error = None
        # pierwsze 133 bity odpowiadają statusowi odblokowania danego avataru
        unlocks_encoded = "0000-0000-0000-0000-0000-0000-0000-0000-0000"
        print(name, generate_password_hash(password), 10000, unlocks_encoded, 0, 0, 0, 0, 0)
        try:
            db.execute(
                'INSERT INTO user (username, password, points, unlocks, \
                abc_best_score, abc_best_time, \
                lost_points, won_points, \
                streamer_bool) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (name, generate_password_hash(password), 10000, unlocks_encoded, 0, 0, 0, 0, 0,),
            )
            db.commit()
        except db.IntegrityError:
            error = 'Trochę niezręcznie ale ktoś już zajął ten nick.'
        return error

    def login(db, name, password):
        error   = None
        user_id = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (name,)
        ).fetchone()

        if user is None:
            error = 'Nie ma takiego użytkownika. Następnym razem spróbuj trafiać w klawisze.'
        elif not check_password_hash(user['password'], password):
            error = 'Tym razem nie udało ci się włamać na czyjeś konto ale nie poddawaj się. Pssst, spróbuj dupa123. Nie ma za co.'
        else:
            user_id = user['id']
        return [error, user_id]

    def username(db, user_id):
        user = db.execute(
            'SELECT username FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        if not user:
            return None
        return user['username']
    
    def id(db, username):
        user = db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone()
        if not user:
            return None
        return user['id']

    def getAvatarId(db, user_id):
        user = db.execute(
            'SELECT avatar_id FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        if not user:
            return None
        return user['avatar_id']

    def setAvatarId(db, user_id, avatar_id):
        error = None
        user = db.execute(
            'SELECT unlocks FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        if not user:
            return 'Nie udało się zmienić avataru.'

        unlocks = user['unlocks'].split('-')

        avatar_block = round(avatar_id / 16)
        avatar_block_id = (avatar_id % 16) * 2
        avatar_block_dec = int('0x' + unlocks[avatar_block], 0)

        if avatar_block_dec & avatar_block_id is False:
            return 'Nie posiadasz tego avataru.'
        
        try:
            db.execute(
                'UPDATE user SET avatar_id = ? WHERE id = ?',
                (avatar_id, user_id,),
            )
            db.commit()
        except db.IntegrityError:
            error = 'Nie baza :('
        return error

    def setUnlocks(db, user_id, unlocks):
        error = None
        try:
            db.execute(
                'UPDATE user SET unlocks = ? WHERE id = ?',
                (unlocks, user_id,),
            )
            db.commit()
        except db.IntegrityError:
            error = 'Nie baza :('
        return error

    def getPoints(db, user_id):
        user = db.execute(
            'SELECT points FROM user WHERE id = ?', (user_id,)
        ).fetchone()

        return user['points']

    def setPoints(db, user_id, points):
        error = None
        try:
            db.execute(
                'UPDATE user SET points = ? WHERE id = ?',
                (points, user_id,),
            )
            db.commit()
        except db.IntegrityError:
            error = 'Nie baza :('
        return error
        
    def getWonLostPoints(db, user_id):
        user = db.execute(
            'SELECT won_points, lost_points FROM user WHERE id = ?', (user_id,)
        ).fetchone()

        return [user['won_points'], user['lost_points']]

    def setWonLostPoints(db, user_id, won_points, lost_points):
        error = None
        try:
            db.execute(
                'UPDATE user SET won_points = ?, lost_points = ? WHERE id = ?',
                (won_points, lost_points, user_id,),
            )
            db.commit()
        except db.IntegrityError:
            error = 'Nie baza :('
        return error

    def setABCStats(db, user_id, score, time):
        error = None

        user = db.execute(
            'SELECT abc_best_score, abc_best_time FROM user_info WHERE id = ?', 
            (user_id,)
        ).fetchone()

        best_score = user['abc_best_score']
        best_time  = user['abc_best_time']

        if score > best_score:
            best_score = score
            best_time = time

        if score == best_score and time < best_time:
            best_time = time

        if best_time != user['abc_best_time']:
            try:
                db.execute(
                    'UPDATE user SET abc_best_score = ?, abc_best_time = ? WHERE id = ?',
                    (best_score, best_time, user_id,)
                )
                db.commit()
            except db.IntegrityError:
                error = 'Nie baza :('
        return error

    def setSvnId(db, user_id, svnid):
        error = None
        try:
            db.execute(
                'UPDATE user SET streamer_svnid = ? WHERE id = ?',
                (svnid, user_id,)
            )
            db.commit()
        except db.IntegrityError:
            error = 'Nie baza :('
        return error

    def getStats(db, user_id):
        user = db.execute(
            'SELECT * FROM user_info WHERE id = ?', (user_id,)
        ).fetchone()

        stats = {
            'id':user['id'],
            'username':user['username'],
            'avatar_id':user['avatar_id'],
            'unlocks':user['unlocks'],
            'points':user['points'],
            'abc_best_score':user['abc_best_score'],
            'abc_best_time':user['abc_best_time'],
            'lost_points':user['lost_points'],
            'won_points':user['won_points'],
            'streamer_bool':user['streamer_bool'],
            'streamer_svnid':user['streamer_svnid']
        }
        return stats

    def getLeaderboard(db, sort_col='points'):
        users_list = db.execute(
            f'SELECT username, points, avatar_id FROM user_info ORDER BY {sort_col} DESC;',
        ).fetchall()

        if not users_list:
            return None

        leaderboard = {
            'entries': 0
        }
        for place, user in enumerate(users_list):
            entry = {
                'username': user['username'],
                'points': user['points'],
                'avatar_id': user['avatar_id']
            }
            leaderboard.update({f'{place}':entry})
            leaderboard.update({'entries': place + 1})
            if place == 99:
                break
        return leaderboard
        

