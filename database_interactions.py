import sqlite3
import os

filename = 'database.db'

'''
def create_db():
    # Creates a brand new database file in case of absense of any .db files in current folder
    if not os.path.exists(os.path.dirname(__file__) + '/*.db'):
        with open(filename, 'w'):
            pass

    with sqlite3.connect(filename) as connection:
        cur = connection.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS Notes (Update_id int, User_id int, Body text, Datetime text)')
'''


def insert_update(update_id, user_id, text, datetime):
    # Inserts the update data and entered information into the database
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO Notes VALUES (?, ?, ?, ?)', (update_id, user_id, text, datetime))
    conn.commit()
    conn.close()


def get_note_by_update_id(update_id):
    # Gets the body of the note by an update_id passed in callback_data, returns text
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT Body FROM Notes WHERE Update_id = ?', (str(update_id),))
    text = cur.fetchone()[0]
    conn.close()

    return text


def get_notes_by_user_id(user_id):
    # Collects all notes of particular user from the database
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT Update_id, Body, Datetime FROM Notes WHERE User_id = ?', (str(user_id),))
    options = cur.fetchall()
    conn.close()

    return options


def get_found_notes_by_update_ids(matching_set):
    # Captures matching notes by screened out update_ids
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    sql_query = "SELECT Update_id, Body, Datetime FROM Notes WHERE Update_id IN" \
                "({seq})".format(seq=','.join(['?'] * len(matching_set)))
    cur.execute(sql_query, tuple(matching_set))
    options = cur.fetchall()
    conn.close()

    return options
