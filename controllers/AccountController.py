from util.db import admin_conn

def get_account_data(username):
    return None

def get_all_users():
    with admin_conn.cursor() as curs:
        curs.execute('select username, account_balance from users')
        return curs.fetchall()