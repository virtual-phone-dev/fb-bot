import asyncio
from playwright.async_api import async_playwright
from outils_playwright import (charger_fichier_d, verifier_nouveau_element, verifier_date_recontacte, mettre_a_jour)
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(        
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-web-security",
            ],
        )
        
        cle_db1 = "page"
        cle_db2 = "fichier"
        
        fichier1 = "pages_collecter.json"
        fichier2 = "pages_collecter2.json"
        pages_fb = await verifier_nouveau_element(fichier1, fichier2, cle_db1)
        
        fichier3 = "mes_comptes_fb.json"
        fichier4 = "mes_comptes_fb2.json"
        comptes_fb = await verifier_nouveau_element(fichier3, fichier4, cle_db2)
        
        fichier_derniere_page = "fichier_page_debut.json"
        derniere_page = (await charger_fichier_d(fichier_derniere_page)).get(cle_db1)
        
        index = next((i for i, page in enumerate(pages_fb) if page[cle_db1] == derniere_page), 0)
        page_suivant = None
        pages_deja_contacter = set()
        tour = 0
        
        if len(comptes_fb) == 0: 
            print("Tout les comptes ont été utilisés") 
        
        for compte_fb in comptes_fb:             
            tour += 1
            print("index ", index)
            for une_page in pages_fb:
                url_page = une_page.get('page')
                name = une_page.get('nom')
                fichier_cookie = compte_fb.get(cle_db2)
                mon_compte = compte_fb.get(cle_db2)
                
                if derniere_page:
                    if derniere_page == name: debut = True
                    if not debut: continue
                
                print("✅", mon_compte); print(name); print(url_page);
                await mettre_a_jour(fichier2, {"ami": 1}, cle_db1, url_page)
                print("Patiente 5s"); await asyncio.sleep(5)

asyncio.run(main())
