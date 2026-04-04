import asyncio
from itertools import cycle;
from playwright.async_api import async_playwright
from outils_playwright import (creer_context, creer_page, aller, envoyer_commentaire, charger_json, post_deja_commente, est_blacklist, ajouter_blacklist, sauvegarder_json)

FICHIER_POSTS = "sauvegarde/posts_commentes.json"
FICHIER_BLACKLIST = "sauvegarde/blacklist.json"



async def visiter(browser, compte, url, comments, posts, blacklist, page_name=None):
    fichier = compte["fichier"]
    if est_blacklist(blacklist, fichier, url): print("Blacklist :", fichier, url); return

    contexte = await creer_context(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        await envoyer_commentaire(page, comments, posts, FICHIER_POSTS, page_name, url, fichier)
        
    except Exception as e:
        print("Erreur :", e)
        ajouter_blacklist(blacklist, FICHIER_BLACKLIST, fichier, url)
        
    await contexte.close()


async def main():
    comptes = charger_json("accounts-fb.json", [])
    pages = charger_json("pages-tout-pays.json", [])
    comments = charger_json("phrase-site-internet.json", [])
    posts = charger_json(FICHIER_POSTS, [])
    blacklist = charger_json(FICHIER_BLACKLIST, {})
    
    # pour choisir la zone ou demarrer
    index_zone = charger_json("index_zone.json", {})
    start_zone = index_zone.get("start_zone")

    start_index = 0
    if start_zone:
        for i, item in enumerate(pages):
            if item.get("zone") == start_zone:
                start_index = i + 1
                print("Démarrage à partir de la zone :", start_zone)
                break
    
    # filtre comptes actifs
    comptes = [c for c in comptes if not c["fichier"].startswith("-")]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        cycle_comptes = cycle(comptes)
        
        while True:
            for page in pages[start_index:]:
                
                # SI C’EST UNE ZONE → ON SAUVEGARDE
                if "zone" in page:
                    print("Nouvelle zone détectée :", page["zone"])
                    sauvegarder_json("index_zone.json", {"start_zone": page["zone"]})
                    continue
        
                if "url" not in page:
                    continue
                await visiter(browser, next(cycle_comptes), page["url"], comments, posts, blacklist, page.get("name"))

asyncio.run(main())

