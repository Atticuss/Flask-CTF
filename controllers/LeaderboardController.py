from util.db import admin_conn

def get_all_leaderboard_data():
    with admin_conn.cursor() as curs:
        curs.execute('select * from leaderboard;')
        return curs.fetchall()

def get_valid_leaderboard_data():
    with admin_conn.cursor() as curs:
        curs.execute('select * from leaderboard where valid=%d;', (1))
        return curs.fetchall()

def get_invalid_leaderboard_data():
    with admin_conn.cursor() as curs:
        curs.execute('select * from leaderboard where valid=%d;', (0))
        return curs.fetchall()  

def get_unique_user_leaderboard_data():
    with admin_conn.cursor() as curs:
        curs.execute('select user_payload, valid from leaderboard;')
        res = curs.fetchall()

    return None

def valid_payload(user, password, student):
    with admin_conn.cursor() as curs:
        curs.execute('insert into leaderboard (user_payload, password_payload, student, valid) values (%s, %s, %s, %s)', (user, password, student, 1))
        admin_conn.commit()

def invalid_payload(user, password, student):
    with admin_conn.cursor() as curs:
        curs.execute('insert into leaderboard (user_payload, password_payload, student, valid) values (%s, %s, %s, %s)', (user, password, student, 0))
        admin_conn.commit()