# This file was run once with the `python3 makeDB.py` command
import sqlite3

conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('DROP TABLE IF EXISTS users')
cur.execute('CREATE TABLE users (username text, password text, email text, firstname text, lastname text)')

conn.commit()
conn.close()
