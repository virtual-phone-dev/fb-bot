import json
import sqlite3

FICHIER_JSON = "pages_collecter_artistes.json"
FICHIER_DB = "pages_collecter_artistes.db"


def creer_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            url TEXT UNIQUE,
            date_collecte DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


# ce script de migrer n'a que 2 champs

def migrer():
    # 1. Charger le JSON existant (une seule fois, c'est la dernière fois
    #    que tu auras besoin de tout charger en RAM d'un coup)
    with open(FICHIER_JSON, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    print(f"{len(donnees)} entrées trouvées dans {FICHIER_JSON}")

    # 2. Connexion SQLite + création de la table
    conn = sqlite3.connect(FICHIER_DB)
    cursor = conn.cursor()
    creer_table(cursor)
    conn.commit()

    # 3. Insertion des entrées
    inserees = 0
    doublons = 0
    erreurs = 0

    for entree in donnees:
        nom = entree.get("nom")
        url = entree.get("url")

        if not url:
            erreurs += 1
            continue

        try:
            cursor.execute(
                "INSERT OR IGNORE INTO pages (nom, url) VALUES (?, ?)",
                (nom, url),
            )
            if cursor.rowcount > 0:
                inserees += 1
            else:
                doublons += 1
        except sqlite3.Error as e:
            print(f"Erreur sur l'URL {url} : {e}")
            erreurs += 1

    conn.commit()
    conn.close()

    print("\n--- Migration terminée ---")
    print(f"Insérées   : {inserees}")
    print(f"Doublons   : {doublons}")
    print(f"Erreurs    : {erreurs}")
    print(f"Base créée : {FICHIER_DB}")


if __name__ == "__main__":
    migrer()