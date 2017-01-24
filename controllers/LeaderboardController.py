from util.db import establish_admin_conn

def get_all_leaderboard_data():
    with establish_admin_conn() as admin_conn:
        with admin_conn.cursor() as curs:
            curs.execute('select * from leaderboard;')
            return curs.fetchall()

def valid_payload(user, password, student):
    with establish_admin_conn() as admin_conn:
        with admin_conn.cursor() as curs:
            curs.execute('insert into leaderboard (user_payload, password_payload, student, valid) values (%s, %s, %s, %s)', (user, password, student, 1))
            admin_conn.commit()

def invalid_payload(user, password, student):
    with establish_admin_conn() as admin_conn:
        with admin_conn.cursor() as curs:
            curs.execute('insert into leaderboard (user_payload, password_payload, student, valid) values (%s, %s, %s, %s)', (user, password, student, 0))
            admin_conn.commit()