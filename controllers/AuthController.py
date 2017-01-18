import hashlib, os, base64, sys
from datetime import datetime
from flask import make_response, redirect, render_template
from util.db import admin_conn
from controllers import LeaderboardController

def authenticate(form_data, student):
    if student is None:
        student = 'anonymous'

    try:
        user = form_data['username']
        password = form_data['password']
    except KeyError:
        return make_response(render_template('login.html', error='Invalid request'), 400)

    m = hashlib.sha1()
    m.update(password.encode())
    hashed_password = base64.b64encode(m.digest()).decode()

    with admin_conn.cursor() as curs:
        try:
            curs.execute('select password from users where username = \'%s\' and password = \'%s\'' % (user, hashed_password))
            res = curs.fetchall()
        except:
            LeaderboardController.invalid_payload(user, password, student)
            return make_response(render_template('login.html', error=sys.exc_info()[1]), 403)

        if len(res) == 0:
            LeaderboardController.invalid_payload(user, password, student)
            return make_response(render_template('login.html', error='Login failed'), 403)
    
        LeaderboardController.valid_payload(user, password, student)

        curs.execute('delete from user_sessions where username=%s', (user))
        admin_conn.commit()

        session_id = base64.b64encode(os.urandom(100))
        creation_time = datetime.strftime(datetime.now(), '%Y-%d-%m %H:%M:%S.%f')
        curs.execute('insert into user_sessions (session_id, username, creation_time) values (%s, %s, %s)', (session_id, user, creation_time))
        admin_conn.commit()

        resp = make_response(redirect('/account'))
        resp.set_cookie('nVisBankingSession', session_id)
        return resp

def validate_session_id(session_id):
    with admin_conn.cursor() as curs:
        curs.execute('select username, creation_time from user_sessions where session_id=%s', (session_id))
        res = curs.fetchall()

        if len(res) > 0:
            session_creation_time = datetime.strptime(res[0][1], '%Y-%d-%m %H:%M:%S.%f')
            delta = datetime.now() - session_creation_time

            if delta.seconds > 3600:
                curs.execute('delete from user_sessions where session_id=%s', session_id)
                admin_conn.commit()

                return None
            else:
                return res[0][0]
        else:
            return None