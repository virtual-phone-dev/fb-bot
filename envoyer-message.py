import json, asyncio, time, msvcrt
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from outils_playwright import (connecter_gmail, charger_cookies, sauvegarder_cookies, sauvegarder_sur_meme_ligne, sauvegarder_fichier, charger_fichier, charger_fichier_d,
basculer_sur_la_page, basculer_sur_le_compte, reparer_fb, ajouter_dans_fichier, mettre_a_jour, verifier_nouveau_element, verifier_date_recontacte, 
clic_div_aria_label_role_button)


PAUSE_MINUTES = 1
format_date = "%d-%m-%Y"

texte = """Partenariat Gagnant-Gagnant

Viens publier tes vidéos sur Florinato, et si tu obtiens 1000 clics sur ta vidéo tu seras payer 2000 dollars.
Si ça t'intéresse, viens sur Florinato, et envoie un message à CAISIP.
https://florinato105.onrender.com """

 
objet = "Partenariat Gagnant-Gagnant"


 


# VERIFIER COMMANDE CONSOLE
async def verifier_commande(page, duree_minutes):
    print("Écrivez..")
    secondes = duree_minutes * 60
    debut = time.time()

    while time.time() - debut < secondes:
        if msvcrt.kbhit():
            cmd = input().strip().lower()

            # passer au compte suivant immédiatement
            if cmd == "+":
                print("compte suivant")
                return

            # pause
            if cmd in ["stop", "-"]:
                print("PAUSE")

                while True:
                    cmd = input("Tape + pour continuer : ").strip()
                    if cmd == "+":
                        print("reprise")
                        debut = time.time()
                        break

        await asyncio.sleep(0.2)
    print("suivant automatique")



async def charger_comptes(fichier_des_comptes):
    with open(fichier_des_comptes, "r", encoding="utf-8") as f:
        return json.load(f)
        
        
async def save_cookies(context):
    print("patiente 7s")
    await asyncio.sleep(7)
    
    print("on sauvegarde les cookies")
    cookies = await context.cookies()
    with open(fichier_cookie, "w") as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)

    print("cookies sauvegardé")
    
    

async def apply_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] }); """)


    
async def envoyer_email(fichier2, fichier4, page, email, mon_email):
    while True:
        try:
            textes = ["Nouveau message", "Compose"]
            trouver = False
            for t in textes:
                
                btn = await page.query_selector(f"text={t}")
                if btn:
                    await btn.click()
                    print("patiente 3s"); await asyncio.sleep(3); 
                    trouver = True
                    break
            if trouver: break
        except:
            pass


    while True:
        try:
            textes = ["Destinataires", "To recipients"]
            trouver = False
            for t in textes:
                
                element = page.locator(f'input[aria-label*="{t}"]')
                if await element.count() > 0:
                    #await element.click()
                    await element.fill(email)
                    trouver = True
                    break
            if trouver: break
        except:
            pass


    while True:
        textes = ["Objet", "Subject"]
        trouver = False
        for t in textes:
            
            element = page.locator(f'input[aria-label="{t}"]')
            if await element.count() > 0:
                await element.fill(objet)
                trouver = True
                break
        if trouver: break
        

    while True:
        textes = ["Corps du message", "Message Body"]
        trouver = False
        for t in textes:
            
            element = page.locator(f'div[aria-label="{t}"]')
            if await element.count() > 0:
                await element.click() #clique pour activer la zone de texte, car contenteditable="true"
                await page.keyboard.type(texte)
                trouver = True
                break
        if trouver: break
        
        
    #print("patiente 10000s"); await asyncio.sleep(10000)
    while True:
        try:
            textes = ["Envoyer", "Send"]
            trouver = False
            for t in textes: 
                
                btn = page.locator(f'div[role="button"][aria-label*="{t}"]')                
                if await btn.count() > 0:
                    await btn.click()
                    trouver = True
                    print("patiente 10s"); await asyncio.sleep(10)
                    await marquer_contact(fichier2, "email", email, jours_recontact=60)
                    await marquer_contact(fichier4, "email", mon_email) #sauvegarde date recontacte de mon compte_email
                    break
            if trouver: break
        except:
            pass
    #print("patiente 10000s"); await asyncio.sleep(10000)



async def tour_suivant(fichier_email_debut, emails, mes_comptes, email_suivant, tour, index, cle_db, element):
    if tour+1 > len(mes_comptes):
        print(f"mes_{element}s {len(mes_comptes)}");
        print(f"tout_mes_{element}s_utiliser");
        return f"tout_mes_{element}s_utiliser"
    else:    
        if index+1 > len(emails): 
            index = 0
                    
            mail_s = emails[index]
            email_suivant = mail_s[cle_db] #print("index e", index); 
            print(f"{element}_suivant : ", email_suivant)  
            print(f"✅ Tous les {element}s ont été utilisés")
            nbre = len(emails); print(f"{nbre} {element}s parmis les {element}s collectés") #break
        else:
            mail_s = emails[index]
            email_suivant = mail_s[cle_db] #print("index e", index); 
            print(f"{element}_suivant : ", email_suivant)  
                            
        data = {cle_db: email_suivant}
        await sauvegarder_fichier(fichier_email_debut, data)
                


async def marquer_contact(fichier, cle_db, cle, jours_recontact=1):
    data = await charger_fichier(fichier) or []

    aujourd_hui = datetime.now()
    relance = aujourd_hui + timedelta(days=jours_recontact)
    
    data_update = { "contacter": aujourd_hui.strftime(format_date), "recontacter": relance.strftime(format_date) }
    
    await mettre_a_jour(fichier, data_update, cle_db, cle)
    



async def envoyer_message(fichier2, fichier4, page, url_page, mon_compte):
    fichier_comptes = "mes_comptes_fb2.json"
    await page.goto(url_page, timeout=0)
    await basculer_sur_le_compte(page, url_page)
    
    #await page.wait_for_load_state("domcontentloaded")
    #print("patiente 5s"); await asyncio.sleep(5) 
    
    statut = await clic_div_aria_label_role_button(page, ["Message"])
    if statut:
        print("bouton message trouvé")
        
        await page.evaluate("""
        const messageButton = document.querySelector('div[aria-label="Message"]'); // cliquer sur le bouton Message, une popup s'ouvre alors , pour ecrire le message
        if (messageButton) { messageButton.click(); } """)
    
        print("Patiente 2s"); await asyncio.sleep(2);
        while True:
            print("Patiente 1s"); await asyncio.sleep(1)
            message_box = page.locator('div[aria-label*="Écrire"]').first
            if await message_box.count() > 0:
                await message_box.fill(texte)        
                    
                print("Patiente 1s"); await asyncio.sleep(1)
                await page.keyboard.press("Enter")

                #print("✅ Message envoyé :", texte);
                
                await marquer_contact(fichier2, "message", url_page, jours_recontact=60)
                await marquer_contact(fichier4, "fichier", mon_compte)
                print("Patiente 10s"); await asyncio.sleep(10)
                break


        
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

        fichier1 = "page_messages_collecter.json"
        fichier2 = "page_messages_collecter2.json"
        pages_fb = await verifier_nouveau_element(fichier1, fichier2, "message") # on verifie si ya de nouveaux emails , pour le mettre dans notre fichier de collectes 
        pages_fb = [p for p in pages_fb if await verifier_date_recontacte(p)]
        
        fichier3 = "mes_comptes_fb.json"
        fichier4 = "mes_comptes_fb2.json"
        comptes_fb = await verifier_nouveau_element(fichier3, fichier4, "message")
        comptes_fb = [c for c in comptes_fb if await verifier_date_recontacte(c) and c.get("message") == 1]; #print("comptes_fb ", comptes_fb) 
        
        fichier_page_message_debut = "fichier_page_message_debut.json"
        page_message_debut = (await charger_fichier_d(fichier_page_message_debut)).get("message")
        
        index = next((i for i, page in enumerate(pages_fb) if page["message"] == page_message_debut), 0) # next() prend le premier résultat trouvé, si un email correspond → retourne son index, sinon → retourne 0 (valeur par défaut) 
        page_suivant = None
        pages_deja_contacter = set()
        tour = 0
        
        #if not len(comptes_fb) > 0: 
        if len(comptes_fb) == 0: 
            print("Tout les comptes ont été utilisés") 
        
        for compte_fb in comptes_fb:             
            tour += 1
            print("index ", index) 
            
           
            if index+1 > len(pages_fb): 
                print("aucune page a contacter, car tous ont deja été contacter", index); break
            
            page = pages_fb[index]
            url_page = page["message"]
            #nom = page["nom"]
            fichier_cookie = compte_fb.get("fichier")
            mon_compte = compte_fb.get("fichier")
            #mon_email = compte_fb.get("email")
            
            if url_page in pages_deja_contacter: continue
            
            context = await browser.new_context() #nouveau contexte pour chaque compte
            cookies = charger_cookies(fichier_cookie) # Charger les cookies AVANT d'ouvrir la page
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            await apply_stealth(page)
            print("✅ mon_compte : ", mon_compte)
            print("Contacté :", url_page)
            
            await envoyer_message(fichier2, fichier4, page, url_page, mon_compte)
            
            pages_deja_contacter.add(url_page)
            index += 1            
            
            statut = await tour_suivant(fichier_page_message_debut, pages_fb, comptes_fb, page_suivant, tour, index, "message", "compte")
            if statut == "tout_mes_comptes_utiliser": break
            
            #print("patiente 10s"); await asyncio.sleep(10)  
            await context.close()

asyncio.run(main())
