import requests

class Streamer():
    def __init__(self, name):
        self.name           = name.lower()
        self.id             = None
        self.chatters       = None
        self.twitchEmotes   = None
        self.sevenTVEmotes  = None
        self.bots           = ['streamelements', 'fossabot', self.name]
    
# =========================================== REQUESTS ===========================================
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
        print("Channels Insert")
        self.dbInsertChannels(db)
        print("Chatters Insert")
        self.dbInsertChatters(db)
        print("Emotes Insert")
        self.dbInsertEmotes(db)
        print("Finish")

    def dbInsertChannels(self, db):
        if not self.name or not self.id:
            return False # Error
        try:
            db.execute(
                "INSERT INTO channels (channel_id, streamer) VALUES (?, ?)",
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
            pass # Error

    def dbInsertChatters(self, db):
        if not self.chatters or not self.id:
            return False # Error
        bot_names = self.bots
        bot_flag = False

        for chatter in self.chatters:

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
            
            tries = 3
            while chatter_id is None and tries:
                self.dbInsertChannelsChatters(db, chatter['name'])
                chatter_id = self.getChatterId(db, chatter['name'])
                tries -= 1
            if chatter_id is None:
                continue # Error

            try:
                db.execute(
                    f"INSERT INTO chatters (chatter_id, messages, watchtime, points) \
                    VALUES (?, ?, ?, ?) \
                    ON CONFLICT (chatter_id) \
                    DO UPDATE SET \
                    messages={chatter['amount']}, watchtime={watchtime}, points={points};",
                    (chatter_id[0], chatter['amount'], watchtime, points),
                )
                db.commit()
            except db.IntegrityError:
                pass # Error
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
            pass # Error
        
    def dbInsertEmotes(self, db):
        if not self.sevenTVEmotes or not self.twitchEmotes or not self.id:
            return False
        emotes = self.sevenTVEmotes + self.twitchEmotes

        for emote in emotes:
            emote_id = self.getEmoteId(db, emote['emote'])
            tries = 3
            while emote_id is None and tries:
                self.dbInsertChannelsEmotes(db, emote['emote'])
                emote_id = self.getEmoteId(db, emote['emote'])
                tries -= 1
            if emote_id is None:
                continue # Error
            
            try:
                db.execute(
                    f"INSERT INTO emotes (emote_id, amount) \
                    VALUES (?, ?) \
                    ON CONFLICT (emote_id) \
                    DO UPDATE SET \
                    amount={emote['amount']};",
                    (emote_id[0], emote['amount']),
                )
                db.commit()
            except db.IntegrityError:
                pass # Error
        return True
# ================================================================================================
