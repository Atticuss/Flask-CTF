import pymssql, hashlib, base64
from random import randrange

admin_conn = None
readonly_conn = None

def establish_admin_conn(app):
    global admin_conn
    
    server = app.config['DB_Server']
    server_port = app.config['DB_Port']
    user = app.config['admin_db_user']
    password = app.config['admin_db_pw']
    db = app.config['Database']

    admin_conn = pymssql.connect(server=server, port=server_port, user=user, password=password, database=db)

def build_schema():
    drop_table('users')
    drop_table('user_sessions')
    drop_table('account_info')
    drop_table('leaderboard')

    with admin_conn.cursor() as curs:
        curs.execute('create table users (ID int PRIMARY KEY NOT NULL IDENTITY(1, 1), username varchar(30) not null, first_name varchar(30), last_name varchar(30), password varchar(100) not null, account_balance int);')
        curs.execute('create table user_sessions (session_id varchar(200) PRIMARY KEY NOT NULL, username varchar(30) not null, creation_time varchar(100));')
        curs.execute('create table leaderboard (ID int PRIMARY KEY NOT NULL IDENTITY(1, 1), user_payload varchar(1000), password_payload varchar(1000), student varchar(50) not null, valid int not null);')

def drop_table(table_name):
    with admin_conn.cursor() as curs:
        try:
            curs.execute('drop table %s' % table_name)
        except:
            pass

def populate_db():
    with admin_conn.cursor() as curs:
        fname = 'Jay'
        lname = 'Sea'
        uname = 'admin'
        pw = 'F8dk3d0f'

        m = hashlib.sha1()
        m.update(pw.encode())
        hashed_pw = base64.b64encode(m.digest())

        curs.execute('insert into users (first_name, last_name, account_balance, username, password) values (%s, %s, %s, %s, %s)', (fname, lname, 0, uname, hashed_pw))
        admin_conn.commit()

        with open('util/users.txt', 'r') as f:
            for l in f:
                fname, lname, account_balance, uname, hashed_pw = l.strip().split('\t')
                curs.execute('insert into users (first_name, last_name, account_balance, username, password) values (%s, %s, %s, %s, %s)', (fname, lname, account_balance, uname, hashed_pw))
        admin_conn.commit()
