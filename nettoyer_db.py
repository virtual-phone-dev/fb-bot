import sqlite3

conn = sqlite3.connect("profils.db")
cur = conn.cursor()

cur.execute("""
DELETE FROM profils
WHERE url LIKE '%/pages/%'
OR url LIKE '%/events/%'
OR url LIKE '%/groups/%'
""")

conn.commit()

print("Liens inutiles supprimés")

conn.close()