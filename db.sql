create table if not exists messages (
    id integer primary key autoincrement,
    chat_id integer,
    user_id integer,
    message_id integer,
    time_of_day TIME
);

create table if not exists users (
    id integer primary key autoincrement,
    user_id integer,
    timezone VARCHAR(50)
);
