from flask import (Flask, 
                    request, 
                    send_file, 
                    Response,
                    make_response,
                    send_from_directory,
                    render_template,
                    redirect)

from util.db import establish_admin_conn

def load_config_file(app):
    with open('ctf.conf', 'r') as f:
        for l in f:
            if len(l.strip()) > 1 and l[0] != '#':
                k,v = l.split('=')
                app.config[k.strip()] = v.strip()

app = Flask(__name__)
load_config_file(app)
establish_admin_conn(app)

from controllers import (AuthController,
                        AccountController,
                        LeaderboardController)

import sys
import bcrypt
import datetime

@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    student = request.cookies.get('student_name')
    if  request.method == 'GET':
        return render_template('login.html', student=student)
    else:
        return AuthController.authenticate(request.form, student)

@app.route('/account', methods=['GET'])
def account_page():
    session_id = request.cookies.get('nVisBankingSession')
    user = AuthController.validate_session_id(session_id)
    print('user - %s' % user)

    if user is None:
        resp = make_response(redirect('/login'))
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(seconds=-1)
        resp.set_cookie('nVisBankingSession', '', expires=expire_date)

        return resp

    account_data = AccountController.get_account_data(user)
    return render_template('account.html', account_data=account_data)

@app.route('/leaderboard', methods=['GET'])
def leaderboard_page(filt=None):
    leaderboard_data = LeaderboardController.get_all_leaderboard_data()
    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)

@app.route('/leaderboard_login', methods=['GET', 'POST'])
def leadboard_login_page():
    if request.method == 'GET':
        return render_template('leaderboard_login.html')
    else:
        try:
            student = request.form['student_name']
        except KeyError:
            return make_response(render_template('leaderboard_login.html', error='Bad request'), 400)

        resp = make_response(redirect('/login'))
        resp.set_cookie('student_name', student)
        return resp

#---- Background Jobs ----#
try:
	from uwsgidecorators import *
	from util.background_jobs import remove_invalid_sessions
	
	@timer(5)
	def remove_invalid_sessions_job():
		with app.app_context():
			remove_invalid_sessions()
except ImportError:
	print('[!] Not running inside uwsgi, background jobs will not run!')

if __name__ == '__main__':
    load_config_file(app)

    with app.app_context():
        if len(sys.argv) > 1:
            if sys.argv[1] == '--build-db':
                from util.db import build_schema, populate_db

                build_schema()
                populate_db()
                
                print('db rebuilt and populated')
        else:
            app.run(debug=True, host='0.0.0.0', port=5000)
    
