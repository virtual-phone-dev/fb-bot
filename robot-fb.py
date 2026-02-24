import asyncio, random
from playwright.async_api import async_playwright
from outils_playwright import (creer_contexte, creer_page, aller, trouver_post, trouver_lien_post, 
ouvrir_commentaire, envoyer_commentaire, pause_random, charger_json, post_deja_commente, ajouter_post, est_blacklist, ajouter_blacklist)

FICHIER_POSTS = "sauvegarde/posts_commentes.json"
FICHIER_BLACKLIST = "sauvegarde/blacklist.json"



async def visiter(browser, compte, url, comments, posts, blacklist):
    fichier = compte["fichier"]
    if est_blacklist(blacklist, fichier, url): print("Blacklist :", fichier, url); return

    contexte = await creer_contexte(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        post = await trouver_post(page)
        lien = await trouver_lien_post(post)

        if post_deja_commente(posts, lien):
            print("Deja commenté :", lien)
            await contexte.close()
            return

        await ouvrir_commentaire(post, page)
        texte = random.choice(comments)
        await envoyer_commentaire(page, texte)
        print("Commentaire envoyé :", lien)

        ajouter_post(posts, FICHIER_POSTS, lien)
        await pause_random(30, 60)

    except Exception as e:
        print("Erreur :", e)
        ajouter_blacklist(blacklist, FICHIER_BLACKLIST, fichier, url)

    await contexte.close()
    

async def main():
    comptes = charger_json("accounts.json", [])
    pages = charger_json("liste-pages-congo.json", [])
    comments = charger_json("phrase-a-commenter.json", [])
    posts = charger_json(FICHIER_POSTS, [])
    blacklist = charger_json(FICHIER_BLACKLIST, {})

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])

        while True:
            for i, page in enumerate(pages):
                compte = comptes[i % len(comptes)]
                await visiter(browser, compte, page["url"], comments, posts, blacklist)

asyncio.run(main())
