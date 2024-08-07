DROP TABLE IF EXISTS channels;
DROP TABLE IF EXISTS channels_chatters;
DROP TABLE IF EXISTS chatters;
DROP TABLE IF EXISTS channels_emotes;
DROP TABLE IF EXISTS emotes;

CREATE TABLE channels (
  channel_id TEXT PRIMARY KEY,
  streamer TEXT UNIQUE NOT NULL
);

CREATE TABLE channels_chatters (
  chatter_id INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id TEXT NOT NULL,
  chatter_name TEXT NOT NULL,
  FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
);

CREATE TABLE chatters (
  chatter_id INTEGER UNIQUE NOT NULL,
  messages INTEGER NOT NULL,
  watchtime INTEGER NOT NULL,
  points INTEGER NOT NULL,
  FOREIGN KEY (chatter_id) REFERENCES channels_chatters (chatter_id)
);

CREATE TABLE channels_emotes (
    emote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT NOT NULL,
    emote TEXT NOT NULL,
    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
);

CREATE TABLE emotes (
  emote_id INTEGER UNIQUE NOT NULL,
  amount INTEGER NOT NULL,
  FOREIGN KEY (emote_id) REFERENCES channels_emotes (Emote_id)
);