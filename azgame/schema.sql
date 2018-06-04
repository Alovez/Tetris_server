drop table if exists auth_user;
create table auth_user (
  id integer primary key autoincrement,
  email text not null,
  nickname text not null,
  password text not null
);

drop table if exists user_score;

create table user_score (
  id integer primary key autoincrement,
  user_id integer not null,
  game_id integer not null,
  high_score integer not null
);

drop table if exists game_mapping;

create table game_mapping (
  id integer primary key autoincrement,
  game_name text not null
);

INSERT into game_mapping VALUES (1, 'Flappy Bird');
INSERT into game_mapping VALUES (2, '2048');
INSERT into game_mapping VALUES (3, 'Tetris');

create table DQN_info (
  id integer primary key autoincrement,
  game_state text not null
)