import sqlite3
conn = sqlite3.connect('seen.db')


# Create seen table
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS seen
              (uid TEXT PRIMARY KEY)''')
conn.commit()
conn.close()


