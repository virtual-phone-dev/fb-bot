import asyncio
from itertools import cycle;
from playwright.async_api import async_playwright
from outils_playwright import (creer_context, creer_page, aller, envoyer_commentaire, charger_json, post_deja_commente, est_blacklist, ajouter_blacklist)

FICHIER_POSTS = "sauvegarde-florinato/posts_commentes.json"
FICHIER_BLACKLIST = "sauvegarde-florinato/blacklist.json"



async def visiter(browser, compte, url, comments, posts, blacklist):
    fichier = compte["fichier"]
    if est_blacklist(blacklist, fichier, url): print("Blacklist :", fichier, url); return

    contexte = await creer_context(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        await envoyer_commentaire(page, comments, posts, FICHIER_POSTS)
        
    except Exception as e:
        print("Erreur :", e)
        ajouter_blacklist(blacklist, FICHIER_BLACKLIST, fichier, url)
        
    await contexte.close()


async def main():
    comptes = charger_json("accounts-florinato.json", [])
    pages = charger_json("pages-tout-pays.json", [])
    comments = charger_json("phrase-florinato.json", [])
    posts = charger_json(FICHIER_POSTS, [])
    blacklist = charger_json(FICHIER_BLACKLIST, {})
    
    # filtre comptes actifs
    comptes = [c for c in comptes if not c["fichier"].startswith("-")]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        cycle_comptes = cycle(comptes)
        
        while True:
            for page in pages:
                await visiter(browser, next(cycle_comptes), page["url"], comments, posts, blacklist)

asyncio.run(main())

