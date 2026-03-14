import sqlite3

def ajouter_profil(url, name, zone):
    conn = sqlite3.connect("profils.db"); cur = conn.cursor()
    cur.execute("""INSERT OR IGNORE INTO profils(url, name, zone) VALUES(?, ?, ?)""", (url, name, zone))
    conn.commit(); conn.close()
    
    