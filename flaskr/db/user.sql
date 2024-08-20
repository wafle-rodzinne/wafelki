DROP TABLE IF EXISTS user;
DROP VIEW IF EXISTS user_info;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  avatar_id INTEGER,
  unlocks TEXT NOT NULL,

  points  INTEGER NOT NULL,
  abc_best_score INTEGER NOT NULL,
  abc_best_time INTEGER NOT NULL,
  lost_points INTEGER NOT NULL,
  won_points INTEGER NOT NULL,
  
  streamer_bool INTEGER NOT NULL,
  streamer_svnid INTEGER
);

CREATE VIEW user_info
AS
SELECT id, username, points, 
  avatar_id, unlocks, 
  abc_best_score, abc_best_time, 
  lost_points, won_points, 
  streamer_bool, streamer_svnid
  FROM user;