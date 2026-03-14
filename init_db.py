
# 1. Créer la base SQLite

import sqlite3

conn = sqlite3.connect("profils.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS profils(id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, name TEXT, zone TEXT, prochain_message TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS messages_jour(date TEXT, compte TEXT, envoyes INTEGER, PRIMARY KEY(date, compte))""")

conn.commit()
conn.close()

print("Base SQLite prête")

