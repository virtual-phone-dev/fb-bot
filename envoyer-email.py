import json, asyncio, time, msvcrt
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from outils_playwright import (connecter_gmail, charger_cookies, sauvegarder_cookies, sauvegarder_sur_meme_ligne, sauvegarder_fichier, charger_fichier, charger_fichier_d,
basculer_sur_la_page, reparer_fb, ajouter_dans_fichier, mettre_a_jour)

PAUSE_MINUTES = 1
format_date = "%d-%m-%Y"
#format_date = "%Y-%m-%d"

texte = """Salut,
Dis à tes abonnés de venir s'inscrire sur Florinato et si tu obtiens 1000 inscriptions avec ton lien tu seras payer 100 dollars. 
ils vont s'inscrire pour regarder des vidéos sur Florinato. 
Si ça t'intéresse, viens sur Florinato, et n'oublie pas d'envoyer un message à CAISIP.

voilà ton lien d'inscription, publies ça sur ta page, en disant à tes abonnés de s'inscrire sur Florinato pour regarder des vidéos.
https://florinato105.onrender.com """


objet = "Invitation, Mai 2026"


# https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&dsh=S939896141%3A1778232595583163&emr=1&flowEntry=ServiceLogin&flowName=GlifWebSignIn&followup=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ifkv=AWa2PatcW4P1ELI77QxDxLqpNZLL0DITFR40AgjDsO35l31vTWNlWMcnvbpJYfKMVZIIqO0XSN1P9A&osid=1&service=mail





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


    
async def envoyer_email(page, email):
    while True:
        await asyncio.sleep(1)
        textes = ["Nouveau message", "Compose"]
        for t in textes:
            
            btn = await page.query_selector(f"text={t}")
            if btn:
                await btn.click()
                print("patiente 3s"); await asyncio.sleep(3)
    
    #await page.fill('input[aria-label="Destinataires"]', 'Ton texte ici')
    await page.locator('input[aria-label="Destinataires"]').fill(email)
    await page.locator('input[aria-label="Objet"]').fill(objet)

    await page.click('div[aria-label="Corps du message"]') #on clique dabord avant d'écrire pour activer la zone de texte, car l'input est en mode contenteditable="true"
    await page.keyboard.type(texte)
    
    print("patiente 2s"); await asyncio.sleep(2)
    #await page.get_by_role("button", name="Envoyer").click() #Cliquer sur le bouton Envoyer



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
    
    #trouver = False
    
    data_update = {
        "contacter": aujourd_hui.strftime(format_date),
        "recontacter": relance.strftime(format_date)
    }
    
    await mettre_a_jour(fichier, data_update, cle_db, cle)

    #for e in data:
    #    if e.get("email") == email_cible:
    #        e["contacter"] = aujourd_hui.strftime(format_date)
    #        e["recontacter"] = relance.strftime(format_date)
    #        trouver = True
    #        break

    #if trouver: 
    #    print("email trouvé ", email_cible)
    #    await mettre_a_jour(fichier, data_update, "email", email_cible)
    #else: 
    #    print("❌ email non trouvé ", email_cible)
    #    await ajouter_dans_fichier(fichier, data, "email", email_cible, "nom")
    
    
        
async def verifier_nouveau_element(fichier1, fichier2):
    emails_collecter = await charger_fichier(fichier1) # Charger le fichier emails_collecter.json et emails_collecter2.json
    emails_collecter2 = await charger_fichier(fichier2)
    
    nouveaux_emails = []
    for element in emails_collecter: # Vérifier si de nouveaux emails sont dans emails_collecter.json
        if not any(element.get("email") == e.get("email") for e in emails_collecter2): #any sert a lire le resultat
            nouveaux_emails.append(element)
    
    if nouveaux_emails: # Si on a de nouveaux emails, les ajouter à emails_collecter2
        emails_collecter2.extend(nouveaux_emails)
        await sauvegarder_sur_meme_ligne(fichier2, emails_collecter2) # Sauvegarder la nouvelle liste dans emails_collecter2.json

    return emails_collecter2
    
    
        
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
        emails = await verifier_nouveau_element(fichier1, fichier2) # on verifie si ya de nouveaux emails , pour le mettre dans notre fichier de collectes 
        emails = [e for e in emails if await verifier_date_recontacte(e)]
        
        fichier3 = "mes_emails.json"
        fichier4 = "mes_emails2.json"
        compte_emails = await verifier_nouveau_element(fichier3, fichier4) 
        compte_emails = [c for c in compte_emails if await verifier_date_recontacte(c)]
        
        fichier_email_debut = "email_debut.json"
        email_debut = (await charger_fichier_d(fichier_email_debut)).get("email")
        
        #get = len(compte_emails)
        #print("get", get) 
        #print("patiente 10s"); await asyncio.sleep(10); 
                
        #emails = [e for e in emails if not str(e.get("fichier", "")).strip().startswith("-")]
        #emails = await trouver_element_debut(fichier_email_debut, "email")
        
        #emails, email_debut = await trouver_element_debut(fichier_emails, fichier_email_debut, "email")

        #page = await context.new_page() # nouvel onglet
        #await apply_stealth(page)
        
        #start_index = 0
        #if email_debut:
        #    if email_debut in emails:
        #        start_index = emails.index(email_debut)
                   
        index = next((i for i, mail in enumerate(emails) if mail["email"] == email_debut), 0) # next() prend le premier résultat trouvé, si un email correspond → retourne son index, sinon → retourne 0 (valeur par défaut) 
        email_suivant = None
        emails_deja_contacter = set()
        #comptes_deja_utiliser = set()
        tour = 0
        
        for compte_email in compte_emails:             
            tour += 1
            print("index a", index) 
            
            if index+1 > len(emails): 
            #if index == 0:
                print("aucun email a contacter, car tous ont deja été contacter", index); break
            
            print("index c", index) 
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
            await connecter_gmail(page, mon_email)
            await envoyer_email(page, email)
            
            #if not await verifier_date_recontacte(mail): continue
            #if await verifier_date_recontacte(mail):
                #print("peut contacter :", email)
            print("Contacté :", email)
            await marquer_contact(fichier2, "email", email, jours_recontact=60)
            emails_deja_contacter.add(email)
            #else:
            #    continue
            
            await marquer_contact(fichier4, "email", mon_email) #sauvegarde date recontacte de mon compte_email
            #comptes_deja_utiliser.add(email)
            
            print("✅ mon_compte : ", mon_email)
            print("email : ", email)            
            print("index d", index) 
            index += 1
            
            statut = await tour_suivant(fichier_email_debut, emails, compte_emails, email_suivant, tour, index)
            if statut == "tout_mes_comptes_gmail_utiliser": break
            
                #context = await browser.new_context() #nouveau contexte pour chaque compte
                #cookies = charger_cookies(fichier_cookie) # Charger les cookies AVANT d'ouvrir la page
                #await context.add_cookies(cookies)
                #page = await context.new_page()
                #await apply_stealth(page)
                
                #await connecter_gmail(page, email)
                #await envoyer_email(page, email)
                
                #await sauvegarder_cookies(context, fichier_cookie) #print("patiente 10000s"); await asyncio.sleep(10000)
                #await context.close()

asyncio.run(main())
