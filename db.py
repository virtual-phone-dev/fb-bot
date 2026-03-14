
# 2. Gestion SQLite

import sqlite3
from datetime import datetime

DB = "profils.db"

def connexion(): return sqlite3.connect(DB)

def profils_a_envoyer(zone):
    conn = connexion(); cur = conn.cursor()
    cur.execute("""SELECT id, url, name FROM profils WHERE zone = ? AND (prochain_message IS NULL OR prochain_message <= DATE('now'))""", (zone,))
    rows = cur.fetchall()
    conn.close()
    return rows


def maj_prochain_message(profil_id, date):
    conn = connexion(); cur = conn.cursor()
    cur.execute("UPDATE profils SET prochain_message = ? WHERE id = ?", (date, profil_id))
    conn.commit(); conn.close()

def messages_envoyes_aujourdhui(compte):
    conn = connexion(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""SELECT envoyes FROM messages_jour WHERE date = ? AND compte = ?""", (today, compte))
    row = cur.fetchone()
    conn.close()
    if row: return row[0]
    return 0

def incrementer_message(compte):
    conn = connexion(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""INSERT INTO messages_jour(date, compte, envoyes) VALUES(?, ?, 1) ON CONFLICT(date, compte) DO UPDATE SET envoyes = envoyes + 1""", (today, compte))
    conn.commit(); conn.close()
	
	