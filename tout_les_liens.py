
import sqlite3
import asyncio


async def exporter_sans_telephone():
    db_path = "pages_collecter_artistes2.db"
    fichier_sortie = "les_liens.txt"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Garde uniquement les lignes où les deux champs sont NULL ou vides
    cur = conn.execute("""
        SELECT nom, url
        FROM pages
        WHERE (telephone_bio IS NULL OR TRIM(telephone_bio) = '')
          AND (telephone_span IS NULL OR TRIM(telephone_span) = '')
    """)

    lignes_sortie = []
    count = 0
    urls_vues = set()

    for item in cur:
        nom = (item["nom"] or "").strip()
        url = (item["url"] or "").strip()

        if url in urls_vues:
            print(f"⚠️ DOUBLON détecté : {nom} ({url})")
            continue
        urls_vues.add(url)

        # Format : nom, lien, ligne vide
        lignes_sortie.append(nom)
        lignes_sortie.append(url)
        lignes_sortie.append("")

        count += 1

    conn.close()

    if not lignes_sortie:
        print("Aucun enregistrement sans téléphone trouvé")
        return

    with open(fichier_sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_sortie))

    print(f"✅ {count} artistes sans téléphone exportés dans {fichier_sortie}")


if __name__ == "__main__":
    asyncio.run(exporter_sans_telephone())
	