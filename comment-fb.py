import asyncio
from itertools import cycle;
from playwright.async_api import async_playwright
from outils_playwright import (creer_context, creer_page, aller, envoyer_commentaire, charger_json, post_deja_commente, sauvegarder_json)

FICHIER_POSTS = "sauvegarde/posts_commentes.json"



async def visiter(browser, compte, url, comments, posts, blacklist, page_name=None):
    fichier = compte["fichier"]

    contexte = await creer_context(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        await envoyer_commentaire(page, comments, posts, FICHIER_POSTS, page_name, url, fichier)
        
    except Exception as e:
        print("..erreur :")
        
    await contexte.close()



async def main():
    comptes = charger_json("comptes-fb.json", [])
    pages = charger_json("pages-tout-pays.json", [])
    comments = charger_json("phrase-site-internet.json", [])
    posts = charger_json(FICHIER_POSTS, [])
    
    # pour choisir la zone ou demarrer
    index_zone = charger_json("index_zone.json", {})
    start_zone = index_zone.get("start_zone")

    start_index = 0
    if start_zone:
        for i, item in enumerate(pages):
            if item.get("zone") == start_zone:
                start_index = i + 1
                print(start_zone)
                break
    
    # filtre comptes actifs
    comptes = [c for c in comptes if not c["fichier"].startswith("-")]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        cycle_comptes = cycle(comptes)
        
        while True:
            for page in pages[start_index:]:
                if "url" not in page: continue
                
                # SI C’EST UNE ZONE → ON SAUVEGARDE
                if "zone" in page:
                    print(page["zone"])
                    sauvegarder_json("index_zone.json", {"start_zone": page["zone"]})
                    continue
        
                await visiter(browser, next(cycle_comptes), page["url"], comments, posts, page.get("name"))

asyncio.run(main())

