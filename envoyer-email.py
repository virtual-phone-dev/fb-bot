import json, asyncio, time, msvcrt
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from outils_playwright import (connecter_gmail, charger_cookies, sauvegarder_cookies, sauvegarder_sur_meme_ligne, sauvegarder_fichier, charger_fichier, charger_fichier_d,
basculer_sur_la_page, reparer_fb, ajouter_dans_fichier, mettre_a_jour)

PAUSE_MINUTES = 1


texte = """Dis à tes abonnés de regarder leur vidéos préférées sur Florinato. 
On paye 100 dollars pour 1000 inscriptions, 1000 personnes qui vont s'inscrire avec ton lien, et tu pourras suivre les statistiques des inscriptions sur ton compte Florinato.
Et si jamais tu crées ton compte Florinato, n'oublie pas d'envoyer un message à CAISIP (sur Florinato).

Si ça t'intéresse, voilà ton lien de Partenaire, tu publies ça sur ta page, en disant à tes abonnés de regarder leur vidéos préférées sur Florinato.
https://florinato105.onrender.com """

objet = "Invitation, Mai 2026"




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



async def verifier_date_recontacte(mail):
    if "recontacte" not in mail: return True
    
    try:
        date_recontacte = datetime.strptime(mail["recontacte"], "%Y-%m-%d")
    except:
        return True
        
    return datetime.now() >= date_recontacte



async def marquer_contact(fichier, email_cible):
    data = await charger_fichier(fichier) or []

    aujourd_hui = datetime.now()
    relance = aujourd_hui + timedelta(days=60)
    
    trouver = False
    
    data_update = {
        "contacter": aujourd_hui.strftime("%Y-%m-%d"),
        "recontacter": relance.strftime("%Y-%m-%d")
    }

    for e in data:
        if e.get("email") == email_cible:
            e["contacter"] = aujourd_hui.strftime("%Y-%m-%d")
            e["recontacter"] = relance.strftime("%Y-%m-%d")
            trouver = True
            break

    if trouver: 
        print("email trouvé ", email_cible)
        await mettre_a_jour(fichier, data_update, "email", email_cible)
    else: 
        print("❌ email non trouvé ", email_cible)
        #await ajouter_dans_fichier(fichier, data, "email", email_cible, "nom")
    
    
    
async def verifier_nouveau_element(fichier1, fichier2):
    emails_collecter = await charger_fichier(fichier1) # Charger le fichier emails_collecter.json et emails_collecter2.json
    emails_collecter2 = await charger_fichier(fichier2)
    
    # Vérifier si de nouveaux emails sont dans emails_collecter.json
    nouveaux_emails = []
    for email in emails_collecter:
        if email not in emails_collecter2:
            nouveaux_emails.append(email)
    
    # Si on a de nouveaux emails, les ajouter à emails_collecter2
    if nouveaux_emails:
        emails_collecter2.extend(nouveaux_emails)
        #await sauvegarder_sur_meme_ligne(fichier2, emails_collecter2) # Sauvegarder la nouvelle liste dans emails_collecter2.json
    
    # Charger la liste d'emails à partir de emails_collecter2.json
    #emails = emails_collecter2
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
        
        fichier3 = "mes_emails.json"
        fichier4 = "mes_emails2.json"
        compte_emails = await verifier_nouveau_element(fichier3, fichier4) 
        
        
        fichier_email_debut = "email_debut.json"
        email_debut = (await charger_fichier_d(fichier_email_debut)).get("email")
                
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
        tour = 0
        
        for compte_email in compte_emails: 
            tour += 1; #print("tour ", tour)
            
            mail = emails[index]
            email = mail["email"]
            nom = mail["nom"]
                                
            mon_email = compte_email.get("email")
            
            #if not await verifier_date_recontacte(mail): continue
            #if await verifier_date_recontacte(mail):
            #    print("peut contacter ")
            #else:
            #    print("ne peut pas contacter ")
                
            await marquer_contact(fichier2, email)
            
            print("✅ mon_compte : ", mon_email)
            print("email : ", email)            
            
            print("index d", index) 
            index += 1
            
            if tour+1 > len(compte_emails):
                print(f"mes_emails {len(compte_emails)}");
                break
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
