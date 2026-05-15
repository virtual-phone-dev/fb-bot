import json, asyncio, time, msvcrt
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from outils_playwright import (connecter_gmail, charger_cookies, sauvegarder_cookies, sauvegarder_sur_meme_ligne, sauvegarder_fichier, charger_fichier, charger_fichier_d,
basculer_sur_la_page, reparer_fb, ajouter_dans_fichier, mettre_a_jour, verifier_nouveau_element)

PAUSE_MINUTES = 1
format_date = "%d-%m-%Y"
#format_date = "%Y-%m-%d"

texte = """Viens publier tes vidéos sur Florinato, et si tu obtiens 1000 clics sur ta vidéo tu seras payer 100 dollars.
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



async def tour_suivant(fichier_email_debut, emails, compte_emails, email_suivant, tour, index):
    if tour+1 > len(compte_emails):
        print(f"mes_emails {len(compte_emails)}");
        print("tout_mes_comptes_gmail_utiliser");
        return "tout_mes_comptes_gmail_utiliser"
    else:    
        if index+1 > len(emails): 
            index = 0
                    
            mail_s = emails[index]
            email_suivant = mail_s["email"] #print("index e", index); 
            print("email_suivant : ", email_suivant)  
            print("✅ Tous les emails ont été utilisés")
            nbre = len(emails); print(f"{nbre} emails parmis les emails collectés") #break
        else:
            mail_s = emails[index]
            email_suivant = mail_s["email"] #print("index e", index); 
            print("email_suivant : ", email_suivant)  
                            
        data = {"email": email_suivant}
        await sauvegarder_fichier(fichier_email_debut, data)
                

async def verifier_date_recontacte(mail):
    if "recontacter" not in mail: return True 
    
    try:
        date_recontacte = datetime.strptime(mail["recontacter"], format_date)
    except:
        return True
        
    return datetime.now() >= date_recontacte



async def marquer_contact(fichier, cle_db, cle, jours_recontact=1):
    data = await charger_fichier(fichier) or []

    aujourd_hui = datetime.now()
    relance = aujourd_hui + timedelta(days=jours_recontact)
    
    data_update = {
        "contacter": aujourd_hui.strftime(format_date),
        "recontacter": relance.strftime(format_date)
    }
    
    await mettre_a_jour(fichier, data_update, cle_db, cle)


        
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

        fichier1 = "emails_collecter.json"
        fichier2 = "emails_collecter2.json"
        emails = await verifier_nouveau_element(fichier1, fichier2, "email") # on verifie si ya de nouveaux emails , pour le mettre dans notre fichier de collectes 
        emails = [e for e in emails if await verifier_date_recontacte(e)]
        
        fichier3 = "mes_emails.json"
        fichier4 = "mes_emails2.json"
        compte_emails = await verifier_nouveau_element(fichier3, fichier4, "email")
        compte_emails = [c for c in compte_emails if await verifier_date_recontacte(c)]
        
        fichier_email_debut = "email_debut.json"
        email_debut = (await charger_fichier_d(fichier_email_debut)).get("email")
        
        index = next((i for i, mail in enumerate(emails) if mail["email"] == email_debut), 0) # next() prend le premier résultat trouvé, si un email correspond → retourne son index, sinon → retourne 0 (valeur par défaut) 
        email_suivant = None
        emails_deja_contacter = set()
        tour = 0
        
        for compte_email in compte_emails:             
            tour += 1
            print("index a", index) 
            
            if index+1 > len(emails): 
                print("aucun email a contacter, car tous ont deja été contacter", index); break
            
            mail = emails[index]
            email = mail["email"]
            nom = mail["nom"]
            fichier_cookie = compte_email.get("fichier")
            mon_email = compte_email.get("email")
            
            if email in emails_deja_contacter: continue
            
            context = await browser.new_context() #nouveau contexte pour chaque compte
            cookies = charger_cookies(fichier_cookie) # Charger les cookies AVANT d'ouvrir la page
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            await apply_stealth(page)
            print("✅ mon_compte : ", mon_email)
            print("Contacté :", email)
            
            statut = await connecter_gmail(context, fichier_cookie, page, mon_email)
            if statut == "erreur_serveur_gmail": await context.close()
                
            await envoyer_email(fichier2, fichier4, page, email, mon_email)
            
            emails_deja_contacter.add(email)
            index += 1
            
            statut = await tour_suivant(fichier_email_debut, emails, compte_emails, email_suivant, tour, index)
            if statut == "tout_mes_comptes_gmail_utiliser": break
                
            #print("patiente 10000s"); await asyncio.sleep(10000)
            await context.close()

asyncio.run(main())
