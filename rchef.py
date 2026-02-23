import os
import shutil
import hashlib
import json

# --- CONFIGURATION ---
FICHIERS_BOT = ["projet41.py", "comments.json", "pages.json", "accounts.json", 
"blacklist.json", "commented_posts.json",
                "cookies.json", "cookies2.json", "cookies8.json", "cookies6.json",
                "cookies7.json", "cookies15.json", "cookies14.json", "cookies13.json",
                "cookies12.json", "cookies10.json", "cookies9.json", "cookies3.json",
                "cookies4.json"]
CHEMIN_FICHIER_SOURCE = "liste.txt"
PAGES_PAR_BOT = 20
DOSSIER_SORTIE = "bots_generes_json"
TEST_BOTS = 2
MAJ_EXISTANTS = True
EXCLURE_FICHIERS = ["pages.json", "comments.json"]

# Fonction pour calculer le hash d’un fichier
def hash_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Fonction pour comparer deux dictionnaires de hashes
def fichiers_modifies(source_hashes, target_hashes):
    # Vérifie si un fichier source a changé ou si un nouveau fichier est présent
    for f in source_hashes:
        if f not in target_hashes or source_hashes[f] != target_hashes[f]:
            return True
    # Vérifie s'il y a des fichiers dans target_hashes qui ne sont pas dans source_hashes
    for f in target_hashes:
        if f not in source_hashes:
            return True
    return False

# Lecture du fichier source
with open(CHEMIN_FICHIER_SOURCE, "r", encoding="utf-8") as f:
    lignes = [line.strip() for line in f if line.strip()]

# Conversion en liste de dicts
nouvelles_pages = []
for i in range(0, len(lignes), 2):
    name = lignes[i]
    url = lignes[i+1]
    nouvelles_pages.append({"name": name, "url": url})

# Création du dossier de sortie s'il n'existe pas
if not os.path.exists(DOSSIER_SORTIE):
    os.makedirs(DOSSIER_SORTIE)

# On va préparer la liste des noms de bots existants pour éviter les doublons
bots_existants = sorted([d for d in os.listdir(DOSSIER_SORTIE)
                         if os.path.isdir(os.path.join(DOSSIER_SORTIE, d))])

# Si le dernier bot a encore de la place, on le complète
if bots_existants:
    dernier_bot = bots_existants[-1]
    dernier_path = os.path.join(DOSSIER_SORTIE, dernier_bot)
    pages_file = os.path.join(dernier_path, "pages.json")
    if os.path.exists(pages_file):
        with open(pages_file, "r", encoding="utf-8") as f:
            pages_existantes = json.load(f)
        espace_restant = PAGES_PAR_BOT - len(pages_existantes)
        a_ajouter = nouvelles_pages[:espace_restant]
        pages_existantes.extend(a_ajouter)
        with open(pages_file, "w", encoding="utf-8") as f:
            json.dump(pages_existantes, f, indent=4, ensure_ascii=False)
        nouvelles_pages = nouvelles_pages[espace_restant:]
        print(f"{dernier_bot} complété avec {len(a_ajouter)} pages.")

# Calculer hash de tous les fichiers source une seule fois
source_hashes = {}
for fichier in FICHIERS_BOT:
    if os.path.exists(fichier):
        source_hashes[fichier] = hash_file(fichier)

# Fonction pour créer ou mettre à jour un bot
def creer_or_update_bot(nom_bot, pages, source_hashes):
    bot_path = os.path.join(DOSSIER_SORTIE, nom_bot)

    # Vérifier si le bot existe déjà
    if os.path.exists(bot_path):
        if MAJ_EXISTANTS:
            # Vérifier si les fichiers ont changé
            target_hashes = {}
            for f in FICHIERS_BOT:
                fichier_dest = os.path.join(bot_path, os.path.basename(f))
                if os.path.exists(fichier_dest):
                    target_hashes[os.path.basename(f)] = hash_file(fichier_dest)

            # Si les fichiers source ont changé, supprimer le dossier pour recréer
            if fichiers_modifies(source_hashes, target_hashes):
                shutil.rmtree(bot_path)
                os.makedirs(bot_path)
            else:
                # Pas besoin de recréer, on met à jour pages.json seulement
                pages_file = os.path.join(bot_path, "pages.json")
                with open(pages_file, "w", encoding="utf-8") as f:
                    json.dump(pages, f, indent=4, ensure_ascii=False)
                print(f"{nom_bot} mis à jour (pages uniquement).")
                return
        else:
            print(f"{nom_bot} existe déjà. MAJ_EXISTANTS est False, pas modifié.")
            return
    else:
        os.makedirs(bot_path)

    # Copier tous les fichiers du bot
    for fichier in FICHIERS_BOT:
        dest_path = os.path.join(bot_path, os.path.basename(fichier))
        shutil.copy(fichier, dest_path)

    # Créer pages.json
    pages_file = os.path.join(bot_path, "pages.json")
    with open(pages_file, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=4, ensure_ascii=False)

    # Créer requirements.txt
    requirements_path = os.path.join(bot_path, "requirements.txt")
    with open(requirements_path, "w", encoding="utf-8") as f:
        f.write("playwright\n")
    print(f"Bot créé ou mis à jour : {nom_bot} ({len(pages)} pages)")

# Boucle de création / mise à jour
index_bot = 1
while nouvelles_pages:
    lot_pages = nouvelles_pages[:PAGES_PAR_BOT]
    nouvelles_pages = nouvelles_pages[PAGES_PAR_BOT:]

    # Vérifier si un dossier du même nom existe déjà
    nom_bot = f"Sagesse {index_bot}"
    bot_path = os.path.join(DOSSIER_SORTIE, nom_bot)

    # La fonction s'en charge de ne pas recréer si déjà existant et pas modifié
    # La fonction s'en charge de ne pas recréer si déjà existant et pas modifié
    creer_or_update_bot(nom_bot, lot_pages, source_hashes)
    index_bot += 1

print("Meta-robot terminé avec succès !")