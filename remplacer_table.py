import sqlite3

conn = sqlite3.connect('profils.db')
cursor = conn.cursor()

# Renommer la table 'profils' en 'listeAmis'
cursor.execute('''
    ALTER TABLE profils RENAME TO listeAmis;
''')

conn.commit()
conn.close()