import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, escape

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


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
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username']) + """<a href="/logout">Logout</a>"""
    return redirect(url_for('login'))
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    # return render_template('show_entries.html', entries=entries)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_c = request.form['password_confirm']
        if password != password_c:
            return render_template('register.html', response_message='Password not same.')
        db = get_db()
        cur = db.execute("select id from auth_user WHERE user_name = '%s'" % username)
        if cur.rowcount != 0:
            password = generate_password_hash(password)
            db.execute("INSERT INTO auth_user (user_name, password) VALUES ('%s', '%s')" % (username, password))
            db.commit()
            flash('Sign up success!')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', response_message='Username is already exist.')
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cur = db.execute("SELECT password FROM auth_user where user_name = '%s'" % username)
        p_db = cur.fetchone()
        print(p_db)
        if cur.rowcount != 0 and p_db:
            if check_password_hash(p_db[0], password):
                session['username'] = username
                return redirect(url_for('index'))
        else:
            flash('Username or Password not match')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()