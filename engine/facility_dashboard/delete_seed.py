import sqlite3

conn = sqlite3.connect('dashboard.db')
c = conn.cursor()
c.execute('DELETE FROM observations')
conn.commit()
print(c.rowcount, 'seed rows deleted')
conn.close()
