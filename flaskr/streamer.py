import requests
from time import time
import random


MAX_TRIES = 3

class SvnEmote():
    def __init__(self, name, id, url, url_alt=None):
        self.name    = name
        self.id      = id
        self.url     = url
        self.url_alt = url_alt

class Streamer():
    def __init__(self, name='unknown', svnid=None):
        self.name           = name.lower()
        self.id             = None
        self.chatters       = None
        self.twitchEmotes   = None
        self.sevenTVEmotes  = None
        self.bots           = ['streamelements', 'fossabot', 'nightbot', self.name]
        self.avatar         = None
        # 7tv Section
        self.svnid          = svnid
        self.svnEmotes      = []
    
# ==================================== STREAMELEMENTS REQUESTS ===================================
    def requestId(self):
        req = requests.get(f'https://api.streamelements.com/kappa/v2/channels/{self.name}')
        if req.status_code != requests.codes.ok:
            return False
        self.id = req.json()['_id']
        return True

    def requestChatStats(self):
        req = requests.get(f'https://api.streamelements.com/kappa/v2/chatstats/{self.name}/stats')
        if req.status_code != requests.codes.ok:
            return False
        self.chatters       = req.json()['chatters']
        self.twitchEmotes   = req.json()['twitchEmotes']
        self.sevenTVEmotes  = req.json()['sevenTVEmotes']
        return True

    def requestPointsWatchtime(self, username):
        req = requests.get(f'https://api.streamelements.com/kappa/v2/points/{self.id}/{username}')
        if not req:
            return [0, 0]
        return [req.json()['points'], req.json()['watchtime']]

    def requestAvatar(self):
        req = str(requests.get(f'https://www.twitch.tv/{self.name}').content)
        tries = 10

        while req.find('<meta property="og:image" content="') == -1 and tries > 0:
            req = str(requests.get(f'https://www.twitch.tv/{self.name}'))
            tries -= 1

        if req.find('<meta property="og:image" content="') == -1:
            from flask import url_for
            self.avatar = url_for('static', filename='img/missing_avatar.png')
            return False

        trash, trash_content = req.split('<meta property="og:image" content="')
        content_with_trash   = trash_content.split('"/>')
        content              = content_with_trash[0]

        self.avatar = content
        return True

    def requestPointsName(self):
        req = requests.get(f'https://api.streamelements.com/kappa/v2/loyalty/{self.id}')
        if req:
            return req.json()['loyalty']['name']
        return 'punkty'
# ================================================================================================

# ========================================== 7TV REQUESTS ========================================
    def request7tvData(self):
        error = None
        for tries in range(MAX_TRIES):
            req = requests.get(f'https://7tv.io/v3/users/{self.svnid}')
            if req.status_code == requests.codes.ok:
                break

        if req.status_code != requests.codes.ok:
            error = 'Request User Error'
            return error

        connection_id = req.json()['connections'][0]['id']

        for tries in range(MAX_TRIES):
            req = requests.get(f'https://7tv.io/v3/users/TWITCH/{connection_id}')
            if req.status_code == requests.codes.ok:
                break
        
        if req.status_code != requests.codes.ok:
            error = 'Request connection Error'
            return error

        self.name = req.json()['username']
        emotes = req.json()['emote_set']['emotes']

        for emote in emotes:
            name    = emote['name']
            data    = emote['data']
            url     = 'https:' + data['host']['url'] + '/4x.webp'
            #url_alt = 'https:' + data['host']['url'] + '/4x_static.webp'

            #if not requests.get(url):# and len(requests.get(url).content) > 0:
            #    print(url)
            #    url     = None
            #if not requests.get(url_alt) and len(requests.get(url_alt).content) > 0:
            #    print(url_alt)
            #    url_alt = None

            #if not url: #and not url_alt:
            #    error = 'One or more emotes does not exists'
            #else:
                #if not url:
                #    id = url_alt.split('/')[-2]
                #    svnEmote = SvnEmote(name, id, url_alt)
                #elif not url_alt:
                #    id = url.split('/')[-2]
                #    svnEmote = SvnEmote(name, id, url)
                #else:
            id = url.split('/')[-2]
            svnEmote = SvnEmote(name, id, url)

            self.svnEmotes.append(svnEmote)
        return error

    def request7tvUsername(svnid):
        for tries in range(MAX_TRIES):
            req = requests.get(f'https://7tv.io/v3/users/{svnid}')
            if req.status_code == requests.codes.ok:
                break
        
        if req.status_code != requests.codes.ok:
            return None
        return req.json()['username']
# ================================================================================================

# =========================================== DB SELECT ==========================================
    def getChatterId(self, db, username):
        chatter_id = db.execute(
            "SELECT * FROM channels_chatters \
             WHERE channel_id = ? \
             AND chatter_name = ?", 
            (self.id, username)
        ).fetchone()
        return chatter_id

    def getEmoteId(self, db, emote):
        emote_id = db.execute(
            "SELECT * FROM channels_emotes \
             WHERE channel_id = ? \
             AND emote = ?", 
            (self.id, emote)
        ).fetchone()
        return emote_id
# ================================================================================================

# =========================================== DB INSERT ==========================================
    def dbInsert(self, db):
        errors = []

        print("Channels Insert")
        if not self.dbInsertChannels(db):
            errors.append('Channels Error')

        print("Chatters Insert")
        if not self.dbInsertChatters(db):
            errors.append('Chatters Error')

        #print("Emotes Insert")
        #if not self.dbInsertEmotes(db):
        #    errors.append('Emotes Error')

        print("Finish")
        return errors

    def dbInsertChannels(self, db):
        if not self.name or not self.id:
            return False # Error
        try:
            db.execute(
                "INSERT OR IGNORE INTO channels (channel_id, streamer) VALUES (?, ?) ",
                (self.id, self.name),
            )
            db.commit()
        except db.IntegrityError:
            return False # Error
        return True

    def dbInsertChannelsChatters(self, db, username):
        try:
            db.execute(
                "INSERT INTO channels_chatters (channel_id, chatter_name) \
                 VALUES (?, ?)",
                 (self.id, username),
            )
            db.commit()
        except db.IntegrityError:
            return False # Error
        return True

    def dbInsertChatters(self, db):
        if not self.chatters or not self.id:
            return False # Error
        bot_names = self.bots
        bot_flag = False
        db_query = []

        start = time()

        for chatter in self.chatters:
            # Removing bots
            for bot_name in bot_names:
                if bot_name == chatter['name']:
                    bot_flag = True
                    break
            if bot_flag:
                bot_names.remove(chatter['name'])
                bot_flag = False
                continue

            points, watchtime = self.requestPointsWatchtime(chatter['name'])
            chatter_id        = self.getChatterId(db, chatter['name'])
            tries             = 3
            while chatter_id is None and tries:
                self.dbInsertChannelsChatters(db, chatter['name'])
                chatter_id = self.getChatterId(db, chatter['name'])
                tries -= 1
            if chatter_id is None:
                continue # Error
            db_query.append((chatter_id[0], chatter['amount'], watchtime,
                             points, chatter['amount'], watchtime, points))
        try:
            db.executemany(
                f"INSERT INTO chatters (chatter_id, messages, watchtime, points) \
                VALUES (?, ?, ?, ?) \
                ON CONFLICT (chatter_id) \
                DO UPDATE SET \
                messages=?, watchtime=?, points=?;",
                db_query,
            )
            db.commit()
        except db.IntegrityError:
            return False # error

        end = time()
        print(f' - Preparing time: {round((end - start)*100)}')

        return True

    def dbInsertChannelsEmotes(self, db, emote):
        try:
            db.execute(
                "INSERT INTO channels_emotes (channel_id, emote) \
                 VALUES (?, ?)",
                 (self.id, emote),
            )
            db.commit()
        except db.IntegrityError:
            return False # Error
        
    def dbInsertEmotes(self, db):
        if not self.sevenTVEmotes or not self.twitchEmotes or not self.id:
            return False
        db_query = []
        emotes = self.sevenTVEmotes + self.twitchEmotes

        start = time()

        for emote in emotes:
            emote_id = self.getEmoteId(db, emote['emote'])
            tries = 3
            while emote_id is None and tries:
                self.dbInsertChannelsEmotes(db, emote['emote'])
                emote_id = self.getEmoteId(db, emote['emote'])
                tries -= 1
            if emote_id is None:
                continue # Error
            db_query.append((emote_id[0], emote['amount'], emote['amount']))
            
        try:
            db.executemany(
                f"INSERT INTO emotes (emote_id, amount) \
                VALUES (?, ?) \
                ON CONFLICT (emote_id) \
                DO UPDATE SET \
                amount=?;",
                db_query,
            )
            db.commit()
        except db.IntegrityError:
            return False # Error

        end = time()
        print(f' - Preparing time: {round((end - start)*100)}')

        return True
# ================================================================================================

# ========================================== 7TV Methods =========================================
    def getSvnEmotesIds(self, name=None):
        shuffled_ids            = []
        tmp_shuffled_svnEmotes  = []

        if self.name == 'unknown':
            if name is None:
                return 'No name Error'
            #get emotes from db
            return 'here will be list from db'
        else:
            tmp_shuffled_svnEmotes = self.svnEmotes

        random.shuffle(tmp_shuffled_svnEmotes)
        for Emote in tmp_shuffled_svnEmotes[:100]:
            shuffled_ids.append(Emote.id)

        return shuffled_ids
# ================================================================================================