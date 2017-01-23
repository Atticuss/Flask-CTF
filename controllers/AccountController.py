from util.db import admin_conn

def get_account_data(username):
    with admin_conn.cursor() as curs:
        curs.execute('select first_name, last_name, account_balance from users where username=%s', (username))
        return curs.fetchall()[0]

def get_all_users():
    with admin_conn.cursor() as curs:
        curs.execute('select username, account_balance from users')
        return curs.fetchall()