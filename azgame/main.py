import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, escape, jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)  # type:Flask
app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.permanent_session_lifetime = timedelta(seconds=60 * 60 * 24 * 15)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


@app.route('/')
def index():
    if 'user' in session:
        return 'Logged in as %s' % escape(session['user']) + """<a href="/logout">Logout</a>"""
    return redirect(url_for('login'))
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    # return render_template('show_entries.html', entries=entries)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nick']
        password = request.form['password']
        password_c = request.form['password_confirm']
        if password != password_c:
            flash('Password not same.')
            return render_template('register.html')
        db = get_db()
        cur = db.execute("select id from auth_user WHERE email='%s'" % email)
        ids = cur.fetchall()
        if not ids:
            password = generate_password_hash(password)
            db.execute(
                "INSERT INTO auth_user (email, nickname, password) VALUES ('%s', '%s', '%s')" % (
                email, nickname, password))
            db.commit()
            flash('Sign up success!')
            return redirect(url_for('login'))
        else:
            flash('Username is already exist.')
            return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.permanent = True
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        app.logger.info(request.form)
        db = get_db()
        cur = db.execute("SELECT password FROM auth_user where email = '%s'" % email)
        p_db = cur.fetchone()
        if p_db:
            if check_password_hash(p_db[0], password):
                session['user'] = email
                return redirect(url_for('index'))
            else:
                flash('Password is not match!')
        else:
            flash('Username is not Exist')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/listuser')
def list_user():
    if 'user' in session:
        db = get_db()
        cur = db.execute("SELECT email FROM auth_user")
        user_list = [user[0] for user in cur.fetchall()]
        return jsonify({"status": 'success', 'user_list': user_list})
    else:
        return jsonify({"status": 'failed'})


if __name__ == '__main__':
    app.run()
