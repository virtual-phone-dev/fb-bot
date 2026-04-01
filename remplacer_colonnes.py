import sqlite3

conn = sqlite3.connect('profils.db')
cursor = conn.cursor()

# Renommer la colonne 'url' en 'lienAmis'
cursor.execute('''
    ALTER TABLE profils RENAME COLUMN url TO lienAmis;
''')

# Renommer la colonne 'zone' en 'monCompte'
cursor.execute('''
    ALTER TABLE profils RENAME COLUMN zone TO monCompte;
''')

conn.commit()
conn.close()