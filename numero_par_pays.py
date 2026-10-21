import sqlite3
import asyncio
import re


def normaliser_numero(numero):
    """Garde uniquement les chiffres, sans '+', '00', espaces ni tirets.
    Ex: '+58424-2245931' -> '584242245931'"""
    chiffres = re.sub(r"\D", "", str(numero))
    if chiffres.startswith("00"):
        chiffres = chiffres[2:]
    return chiffres


async def exporter_numeros_par_pays():
    db_path = "pages_collecter_artistes2.db"

    # 1. Demande l'indicatif dans la console
    saisie = input("Indicatif du pays (ex: 244) : ").strip()
    code = normaliser_numero(saisie)

    if not code:
        print("❌ Indicatif vide ou invalide")
        return

    fichier_sortie = f"numeros_{code}.txt"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cur = conn.execute("""
        SELECT nom, url, telephone_bio, telephone_span
        FROM pages
    """)

    lignes_sortie = []
    count_numeros = 0
    urls_vues = set()

    for item in cur:
        nom = (item["nom"] or "").strip()
        url = (item["url"] or "").strip()

        # 2. Ne garde que les numéros qui commencent par l'indicatif demandé
        numeros = []
        for champ in ("telephone_bio", "telephone_span"):
            valeur = item[champ]
            if not valeur:
                continue
            if normaliser_numero(valeur).startswith(code) and valeur not in numeros:
                numeros.append(valeur)

        if not numeros:
            continue

        if url in urls_vues:
            print(f"⚠️ DOUBLON détecté : {nom} ({url})")
        urls_vues.add(url)

        # 3. Format : nom, numéro(s), lien, ligne vide
        lignes_sortie.append(nom)
        lignes_sortie.extend(numeros)
        lignes_sortie.append(url)
        lignes_sortie.append("")

        count_numeros += len(numeros)

    conn.close()

    if not lignes_sortie:
        print(f"Aucun numéro trouvé pour l'indicatif {code}")
        return

    with open(fichier_sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_sortie))

    print(f"✅ {count_numeros} numéros exportés (artistes uniques: {len(urls_vues)}) dans {fichier_sortie}")


if __name__ == "__main__":
    asyncio.run(exporter_numeros_par_pays())
	