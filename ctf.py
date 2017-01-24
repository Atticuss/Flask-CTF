from flask import (Flask, 
                    request, 
                    send_file, 
                    Response,
                    make_response,
                    send_from_directory,
                    render_template,
                    redirect)

from util.db import set_app

def load_config_file(app):
    with open('ctf.conf', 'r') as f:
        for l in f:
            if len(l.strip()) > 1 and l[0] != '#':
                k,v = l.split('=')
                app.config[k.strip()] = v.strip()

app = Flask(__name__)
load_config_file(app)
set_app(app)

from controllers import (AuthController,
                        AccountController,
                        LeaderboardController)

import sys
import bcrypt
import datetime

# ---
# If running inside uwsgi+nginx, kick off background jobs.
# If not, make sure Flask has routes to handle static files.
# ---

try:
    #---- Background Jobs ----#
    from uwsgidecorators import *
    from util.background_jobs import remove_invalid_sessions

    @timer(5)
    def remove_invalid_sessions_job():
        with app.app_context():
            remove_invalid_sessions()
except ImportError:
    print('[!] Not running inside uwsgi. Background jobs will not run.')

#---- Static File Routes ----#
@app.route('/lib/bootstrap/css/<path:path>')
def sendBootstrapCSS(path):
    return send_from_directory('lib/bootstrap/css', path)

@app.route('/lib/bootstrap/fonts/<path:path>')
def sendBootstrapFonts(path):
    return send_from_directory('lib/bootstrap/fonts', path)

@app.route('/lib/bootstrap/js/<path:path>')
def sendBootstrap(path):
    return send_from_directory('lib/bootstrap/js', path)

@app.route('/lib/jquery/<path:path>')
def sendJQuery(path):
    return send_from_directory('lib/jquery', path)

#---- Dynamic Python outes ----#    

@app.route('/', methods=['GET'])
def welcome_page():
    student = request.cookies.get('student_name', 'anonymous')
    return render_template('welcome.html', student=student)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    student = request.cookies.get('student_name')
    if  request.method == 'GET':
        return render_template('login.html', student=student)
    else:
        return AuthController.authenticate(request.form, student)

@app.route('/account', methods=['GET'])
def account_page():
    student = request.cookies.get('student_name', 'anonymous')
    session_id = request.cookies.get('nVisBankingSession')
    user = AuthController.validate_session_id(session_id)

    if user is None:
        resp = make_response(redirect('/login'))
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(seconds=-1)
        resp.set_cookie('nVisBankingSession', '', expires=expire_date)

        return resp
    elif user == 'admin':
        user_list = AccountController.get_all_users()
        return render_template('user_management.html', student=student, user_list=user_list, user=user)
    else:
        account_data = AccountController.get_account_data(user)
        return render_template('account.html', student=student, account_data=account_data, user=user)

@app.route('/leaderboard', methods=['GET'])
def leaderboard_page(filt=None):
    student = request.cookies.get('student_name', 'anonymous')
    leaderboard_data = LeaderboardController.get_all_leaderboard_data()

    unique_user_payloads = {}
    unique_pw_payloads = {}
    for row in leaderboard_data:
        try:
            t = unique_user_payloads[row[1]]
            c = t[0] + 1
            unique_user_payloads[row[1]] = (c, t[1])
        except KeyError:
            t = (1, row[4])
            unique_user_payloads[row[1]] = t

        try:
            t = unique_pw_payloads[row[2]]
            c = t[0] + 1
            unique_pw_payloads[row[2]] = (c, t[1])
        except KeyError:
            t = (1, row[4])
            unique_pw_payloads[row[2]] = t

    return render_template('leaderboard.html', student=student, leaderboard_data=leaderboard_data, unique_user_payloads=unique_user_payloads, unique_pw_payloads=unique_pw_payloads)

@app.route('/student_registration', methods=['GET', 'POST'])
def leadboard_login_page():
    student = request.cookies.get('student_name', 'anonymous')
    if request.method == 'GET':
        return render_template('leaderboard_login.html', student=student)
    else:
        try:
            student = request.form['student_name']
        except KeyError:
            return make_response(render_template('leaderboard_login.html', student=student, error='Bad request'), 400)

        resp = make_response(redirect('/login'))
        resp.set_cookie('student_name', student)
        return resp

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
    
