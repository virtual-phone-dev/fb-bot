import asyncio
from playwright.async_api import async_playwright
from outils_playwright import (charger_fichier_d, verifier_nouveau_element, verifier_date_recontacte, mettre_a_jour, appliquer_stealth, 
charger_cookies, ajouter_dans_fichier, nettoyer_texte, mots_inutiles)


async def email(page, nom_page, url):           
    element = await page.query_selector('[href^="mailto:"]') # recuperer email
    
    email = None
    if element:
        href = await element.get_attribute("href")
        
        if href:
            email = href.replace("mailto:", "").strip()
            
            if email.endswith("gmail.com"):
                print("email :", email)
                await ajouter_dans_fichier("emails_collecter.json", {"email": email, "nom": nom_page}, "email", email)
                await ajouter_dans_fichier("emails_collecter2.json", {"email": email, "nom": nom_page, "moins_connu": 1}, "email", email)
                await mettre_a_jour("pages_collecter2.json", {"email": 1, "moins_connu": 1}, "page", url)
    
    
    
async def ami(fichier2, page, nom, url_page):
    btn_follower = await page.evaluate("""() => { return [...document.querySelectorAll('span')].find(el => el.innerText.includes("Followers")); } """)
    if btn_follower:
        #print("pas ami")
        
        if "Compte vérifié" in nom:
            print("Compte vérifié")
        else:
            #print("Non vérifié")
            nom_clean = await nettoyer_texte(nom)
                    
            if not any(n in nom_clean for n in mots_inutiles): # si n = nom_compte . nom_compte nest pas dans mots_inutiles, alors tu l'enregistres
                await mettre_a_jour(fichier2, {"ami": 0}, "page", url_page)
                await email(page, nom, url_page)
                #await message(page, nom, url)
    else:
        print("ami")
        await mettre_a_jour(fichier2, {"ami": 1}, "page", url_page)
        await email(page, nom, url_page)
       
        
        
async def visiter_page(context, fichier2, nom, url_page):
    try:
        new_page = await context.new_page()
        await new_page.goto(url_page, timeout=0)
        await ami(fichier2, new_page, nom, url_page)

    except Exception as e:
        print("cc..");print(e)

    finally:
        if new_page:
            await new_page.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(        
            headless=True,
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
        debut = False
        
        index = next((i for i, page in enumerate(pages_fb) if page[cle_db1] == derniere_page), 0)
        page_suivant = None
        pages_deja_contacter = set()
        tour = 0
        
        if len(comptes_fb) == 0: 
            print("Tout les comptes ont été utilisés") 
        
        for compte_fb in comptes_fb:             
            tour += 1
            print("index ", index)
            # Charger les cookies AVANT d'ouvrir la page
            fichier_cookie = compte_fb.get(cle_db2)
            mon_compte = compte_fb.get(cle_db2)
            print("✅", mon_compte);
            
            context = await browser.new_context()
            cookies = charger_cookies(fichier_cookie)
            await context.add_cookies(cookies)
                
            page = await context.new_page()
            await appliquer_stealth(page)
            await page.goto("https://fb.com", timeout=0)

            for une_page in pages_fb:
                url_page = une_page.get('page')
                name = une_page.get('nom')
                
                if derniere_page:
                    if derniere_page == name: debut = True
                    if not debut: continue
                
                print(name); print(url_page);
                await visiter_page(context, fichier2, name, url_page)

asyncio.run(main())
