import sqlite3
conn = sqlite3.connect("pages_collecter_artistes.db")
conn.execute("ALTER TABLE pages ADD COLUMN ami INTEGER")
conn.commit()
conn.close()