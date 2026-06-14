import asyncio
from itertools import cycle;
from playwright.async_api import async_playwright
from outils_playwright import (creer_context, creer_context2, creer_page, aller, envoyer_commentaire_bs, post_deja_commente, charger_fichier, charger_fichier_d, 
verifier_nouveau_element, sauvegarder_json)

FICHIER_POSTS = "sauvegarde-bs/posts_commentes.json"


async def visiter(browser, compte, url, posts, page_name=None):
    fichier = compte["fichier"]

    contexte = await creer_context2(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        await envoyer_commentaire_bs(page, posts, FICHIER_POSTS, page_name, url, fichier)
        
    except Exception as e:
        print("erreur..", e)
        
    await contexte.close()



async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        
        fichier3 = "mes_comptes_bs.json"
        fichier4 = "mes_comptes_bs2.json"
        comptes = await verifier_nouveau_element(fichier3, fichier4, "email")
        
        pages = await charger_fichier("pages-tout-pays-bs.json")
        posts = await charger_fichier(FICHIER_POSTS)
        
        # pour choisir la zone ou demarrer
        fichier_debut = "index_zone_bs.json"
        start_zone = (await charger_fichier_d(fichier_debut)).get("start_zone")

        start_index = 0
        if start_zone:
            for i, item in enumerate(pages):
                if item.get("zone") == start_zone:
                    start_index = i + 1
                    print("Démarrage à partir de la zone :", start_zone)
                    break
        
        comptes = [c for c in comptes if not c["fichier"].startswith("-")] # filtre comptes actifs    
        cycle_comptes = cycle(comptes)
        
        while True:
            for page in pages[start_index:]:
                compte = next(cycle_comptes)
                
                # SI C’EST UNE ZONE → ON SAUVEGARDE
                if "zone" in page:
                    print("Nouvelle zone détectée :", page["zone"])
                    sauvegarder_json("index_zone_bs.json", {"start_zone": page["zone"]})
                    continue
        
                if "url" not in page: continue
                await creer_context(browser, compte)
                await visiter(browser, compte, page["url"], posts, page.get("name"))

asyncio.run(main())
