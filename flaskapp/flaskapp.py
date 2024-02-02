from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

DATABASE = '/var/www/html/flaskapp/users.db'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secret key' # Needed to use session

def connect_to_database():
  return sqlite3.connect(app.config['DATABASE'])

def get_db():
  db = getattr(g, 'db', None)
  if db is None:
    db = g.db = connect_to_database()
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

def execute_query(query, args=()):
  cur = get_db().execute(query, args)
  rows = cur.fetchall()
  cur.close()
  return rows

@app.route('/')
def profile():
  # If the user is already saved in the session, show their profile details
  if session and session['username'] and session['firstname'] and session['lastname'] and session['email']:
    return render_template('index.html')

  # If the user is not in the session, make them log in
  else:
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
  error = ''
  # If the user has submitted the form, attempt to log in
  if request.method == 'POST':
    accounts = execute_query('SELECT * FROM users WHERE username = ? AND password = ?', [request.form['username'], request.form['password']])
    if accounts and accounts[0]:
      # Save everything but the password to the session
      this_account = accounts[0]
      session['username'] = this_account[0]
      session['email'] = this_account[2]
      session['firstname'] = this_account[3]
      session['lastname'] = this_account[4]

      return redirect(url_for('profile'))
    else:
      error = 'Invalid username or password.'
  return render_template('login.html', error = error)

@app.route('/logout')
def logout():
  # When the user logs out, remove them from the session and redirect them to the login page
  session.pop('email', None)
  session.pop('firstname', None)
  session.pop('lastname', None)
  session.pop('username', None)
  return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
  error = ''

  # If the user has submitted the form...
  if request.method == 'POST':
    # Get the data from the form
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    firstname = request.form['firstname']
    lastname = request.form['lastname']

    # Check if the user already exists
    accounts = execute_query('SELECT * FROM users WHERE username = ?', [username])
    if accounts and accounts[0]:
      error = 'An account with that username already exists.'
    else:
      # If the user doesn't exist, add them to the database
      conn = connect_to_database()
      cur = conn.cursor()
      results = cur.execute('INSERT INTO users VALUES (?,?,?,?,?)', [username, password, email, firstname, lastname])
      conn.commit()
      conn.close()

      # If the save is successful, add them to the session and redirect them to the profile page
      if results:
        session['username'] = username
        session['email'] = email
        session['firstname'] = firstname
        session['lastname'] = lastname
        return redirect(url_for('profile'))
      else:
        error = 'Unable to save profile. Try again.'
  return render_template('register.html', error = error)


if __name__ == '__main__':
  app.run()
