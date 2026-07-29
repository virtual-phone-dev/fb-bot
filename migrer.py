import json, sqlite3

FICHIER_JSON = "pages_collecter_artistes2.json"
FICHIER_DB = "pages_collecter_artistes2.db"


def creer_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            url TEXT UNIQUE,
            telephone TEXT,
            telephone_bio TEXT,
            telephone_span TEXT,
            date_collecte DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


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
        # les champs telephone* sont parfois absents, parfois à 0 (int),
        # parfois une vraie chaîne : on normalise tout en texte
        telephone = entree.get("telephone")
        telephone_bio = entree.get("telephone_bio")
        telephone_span = entree.get("telephone_span")

        telephone = str(telephone) if telephone not in (None, 0) else None
        telephone_bio = str(telephone_bio) if telephone_bio else None
        telephone_span = str(telephone_span) if telephone_span else None

        if not url:
            erreurs += 1
            continue

        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO pages (nom, url, telephone, telephone_bio, telephone_span)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nom, url, telephone, telephone_bio, telephone_span),
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