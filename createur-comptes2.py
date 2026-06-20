import json, asyncio, os, sys, msvcrt, time
from playwright.async_api import async_playwright
from outils_playwright import (connecter_gmail, charger_fichier, ajouter_dans_fichier, connexion_bs, query_selector_text, query_selector_a_text, 
div_data_testid, div_data_pagelet, button_id, button_button_text, button_submit_text, input_name, input_type, input_id, span_has_text, connexion_tu)


mot_de_passe = "Diel2019@#"
email = "abdelilluminati@gmail.com"
nom = "Queen Fleurina" 
username = "Queen_Fleurina" 
nom1 = "Queen" 
nom2 = "Fleurina" 

url_post = "https://www.threads.com/@les_luxueux_du_congo/"

url_au = "https://audiomack.com/"
url_su = "https://substack.com/signup?utm_source=reader-cta&utm_medium=web&utm_campaign=home&utm_content=explore-sidebar"
url_insta = "https://www.instagram.com/accounts/emailsignup/?next="
url_li = "https://www.linkedin.com/signup/cold-join/?lipi=urn%3Ali%3Apage%3Ad_flagship3_login%3BRHQKdL8PSAGa2TJzJukqoA%3D%3D"
url_parler = "https://app.parler.com/login"
url_minds = "https://www.minds.com"
url_go = "https://www.goafricaonline.com/inscription"
url_you = "https://www.youtube.com"
url_tu = "https://www.tumblr.com/register?redirect_to=%2Fdashboard%2Fblog%2Fzk-j" # pas de date , au niveau des posts

url_bo = "https://www.boomplay.com/songs/213391263?from=search" # ici il montre le pays
url_mi = "https://www.mixcloud.com/brooklynradio/oonops-drops-brainforests/" # ici ce que jai vu, en general cest beaucoup plus, les radio avec leur emissions en ligne, mais ya des commentaires des gens de uk et autres anglophones. ya aussi les dj 
#url_ = "https://bandcamp.com/" les gar ci affiche les ventes des cd en temps reel , mais jai pas vu les commentaires, ni la partie commentaire. je garde juste pour un jour mettre cet idee dafficher les ventes en temps reel
# on laisse tomber substack, car pour se connecter a chaque compte , ya des "je ne suis pas un robot" qui font chier
# mewe aussi deconne trop, le site reste bloqué
#url_ = ""

# Ma passion c'est la création d'applications mobile
# Création d'applications mobile et de site internet



async def visiter_de(page): # deepai
    await page.goto("https://deepai.org", timeout=0)


async def bs(page): # blue sky
    try:
        await creer_bs(page)
    except Exception as e:
        print("..erreur -bs"); print(e)
        
        
async def creer_bs(page): # blue sky
    #await page.goto("https://bsky.app", timeout=0)
    email = "jefflambo298@gmail.com"; mot_de_passe = "Diel2019@#"
    await connexion_bs(page, email, mot_de_passe)
    await collecter_bs(page)


async def collecter_bs(page):   
    statut = await div_data_testid(page, ["contentHider-post"])
    if statut:
        print("posts trouvés")
    else:
        print("posts pas trouvés")


async def go(page): # goafrica
    try:
        await connexion_go(page)
    except Exception as e:
        print("..erreur -go"); print(e)


async def connexion_go(page): 
    await page.goto("https://www.goafricaonline.com", timeout=0)
    await button_id(page, ["Zsl8fRiKsZ"], clic=True)
    
async def creer_go(page): 
    await page.goto(url_go, timeout=0)
    
    
    
async def insta(page, context): # instagram
    try:
        email="kfhilluminati@gmail.com"; mot_de_passe="Diel2019@#"; nom_profil="Caroline_.1145"; compte="cookies-insta/Caroline.json"; 
        fichier_des_comptes = "mes_comptes_insta2.json"
        
        await page.goto("https://www.instagram.com", timeout=0)  
        await connecter_compte_insta(page, context, compte, fichier_des_comptes, email, mot_de_passe, nom_profil) # connexion_insta
        
        await page.goto("https://www.instagram.com/marine_lepen/", timeout=0)
    except Exception as e:
        print("..erreur -insta"); print(e)
    
    
async def connexion_insta(page): 
    await page.goto("https://www.instagram.com", timeout=0)  

   
async def creer_insta(page):
    await page.goto(url_insta, timeout=0)
    
    
    
async def li(page): # linkedin
    try:
        await connexion_li(page) 
    except Exception as e:
        print("..erreur -linkedin"); print(e)
    
    
async def connexion_li(page): 
    await page.goto("https://www.linkedin.com/login/fr/", timeout=0)
    #await query_selector_text(page, ["S’identifier avec un e-mail"], clic=True)
    
    await input_type(page, ["email"], email)
    await input_type(page, ["password"], mot_de_passe) 
    await span_has_text(page, ["S’identifier"], clic=True)
    
    
async def creer_li(page): # linkedin
    await page.goto(url_li, timeout=0)
    
    await input_name(page, ["email-address"], email)
    await input_name(page, ["password"], mot_de_passe)
    await query_selector_text(page, ["Accepter et s’inscrire"], clic=True, p=15)
    
    await input_name(page, ["first-name"], nom1)
    await input_name(page, ["last-name"], nom2)
    await button_id(page, ["join-form-submit"], clic=True)


    
async def minds(page): # minds
    try:
        await creer_minds(page)
    except Exception as e:
        print("..erreur - minds"); print(e)
        
        
async def creer_minds(page): # minds
    try:
        await page.goto(url_minds, timeout=0) 
        
        await query_selector_text(page, ["Join Now"], clic=True, p=3)    
        await query_selector_a_text(page, ["Join Minds Now"], clic=True)
        
        await input_id(page, ["username"], username, clic=True)
        await input_id(page, ["email"], email, clic=True)
        await input_id(page, ["password"], mot_de_passe, clic=True)
        await input_id(page, ["password2"], mot_de_passe, clic=True)
        await input_type(page, ["checkbox"], clic=True)
    except Exception as e:
        print("..erreur -minds"); print(e)
    


async def pa(page): # parler
    try:
        await connexion_inscription_parler(page)
    except Exception as e:
        print("..erreur -parler"); print(e)

    
async def connexion_inscription_parler(page): # parler , la connexion et l'inscription cest la meme popup, c'est lié
    await page.goto(url_parler, timeout=0)
    
    await input_id(page, ["email"], email)
        
    element = await page.query_selector('button[type="submit"]:has-text("Continue")')
    if element:
        await element.click()
        print("clic reussi - parler.com");   
        


async def pi(page): # pinterest
    try:
        await creer_pi(page)
    except Exception as e:
        print("..erreur -pinterest"); print(e)
        
        
async def creer_pi(page): # pinterest
    await page.goto("https://www.pinterest.com", timeout=0)
    
    await query_selector_text(page, ["S’inscrire"], clic=True, p=3)    
    await input_type(page, ["email"], email)
    await input_type(page, ["password"], mot_de_passe)
    
        
        
async def th(page): # threads
    try:
        email="dgjilluminati@gmail.com"; mot_de_passe="Diel2019@#"
        await connexion_th(page, email, mot_de_passe)
        await collecter_th(page)
    except Exception as e:
        print("..erreur -threads"); print(e)


async def creer_th(page): # threads
    await page.goto("https://www.threads.com", timeout=0)
   

async def collecter_th(page):   
    await page.goto("https://www.threads.com/@jlmelenchon", timeout=0)
    
    statut = await div_data_pagelet(page, ["threads_feed"])
    if statut:
        print("posts trouvés")
    else:
        print("posts pas trouvés")


        
async def tu(page): # tumblr
    try:
        await connexion_tu(page)
        await page.goto("https://www.tumblr.com/communities/french-learners", timeout=0)        
    except Exception as e:
        print("..erreur -tumblr"); print(e)
    
  
async def creer_tu(page): # tumblr
    await page.goto(url_tu, timeout=0)
    
    await input_name(page, ["email"], email)
    await input_name(page, ["password"], mot_de_passe)
    await span_has_text(page, ["Inscription"], clic=True) 
   
   
   
async def wa(page): # wattpad
    try:
        await creer_wat(page)
    except Exception as e:
        print("..erreur -wattpad"); print(e)

        
async def creer_wat(page): 
    await page.goto("https://www.wattpad.com", timeout=0)
    print("patiente 2s"); await asyncio.sleep(2)



async def you(page): # youtube
    try:
        await creer_you(page)
    except Exception as e:
        print("..erreur -youtube"); print(e)   
        
        
async def creer_you(page): # youtube
    await page.goto(url_you, timeout=0)    

    
    

async def verifier_commande(duree_minutes):    
    secondes = duree_minutes * 1
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
    
    
    

async def formatter(data, fichier_des_comptes):
    with open(fichier_des_comptes, "w", encoding="utf-8") as f:
        f.write("[\n")

        for i, item in enumerate(data):
            ligne = json.dumps(item, ensure_ascii=False)

            if i < len(data) - 1:
                f.write(f"    {ligne},\n")
            else:
                f.write(f"    {ligne}\n")

            if (i + 1) % 5 == 0:
                f.write("\n")

        f.write("]")
        

async def charger_comptes(fichier_des_comptes):
    with open(fichier_des_comptes, "r", encoding="utf-8") as f:
        return json.load(f)
        
        
    
async def marquer_creer(compte, fichier_des_comptes):
    with open(fichier_des_comptes, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        if item["fichier"] == compte["fichier"]:
            item["creer"] = "Oui"

    await formatter(data, fichier_des_comptes)
        
        
        
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


        
def load_cookies(fichier_des_comptes):
    with open(fichier_des_comptes, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)

    cookies = []
    for c in raw_cookies:
        cookies.append(
            {
                "name": c.get("name"),
                "value": c.get("value"),
                "domain": c.get("domain"),
                "path": c.get("path", "/"),
                "httpOnly": c.get("httpOnly", False),
                "secure": c.get("secure", False),
                "expires": c.get("expirationDate", -1),
            }
        )
    return cookies



async def reparer_th(page, context, nom_complet, email, mot_de_passe):
    print(f"reparer {nom_complet}")
    await connexion_th(page, email, mot_de_passe)
    
    count = 0
    while count < 3:       
        print("patiente 5s"); await asyncio.sleep(5)            
        element = await page.query_selector("text=Une erreur s’est produite, veuillez réessayer plus tard.")
        if element:
            print("désactiver")
            await context.close()
        count += 1

            
            
async def verifier_blocage_th(page):
    #print("patiente 1s"); await asyncio.sleep(1)  
    #element = await page.query_selector('span[aria-label="Confirmez que vous êtes bien une personne réelle"]')    
    element = await page.query_selector("text=Confirmez que vous êtes une personne réelle")
    if element:
        return "compte_désactiver"
        
        
    element = await page.query_selector("text=Confirmez que vous êtes bien une personne réelle")
    if element:
        return "compte_désactiver"
        
        
        
async def connexion_th(page, email, mot_de_passe):
    try:
        await page.goto("https://www.threads.com/login", timeout=0)
    except:
        print("recharge la page")
        await page.goto("https://www.threads.com/login", timeout=0)
        
    while True:
        input_box = page.get_by_placeholder("Nom de profil, numéro de mobile ou e-mail")
        if await input_box.count() > 0:            
            await input_box.fill(email)
            break
            
    while True:
        input_box = page.get_by_placeholder("Mot de passe")
        if await input_box.count() > 0:            
            await input_box.fill(mot_de_passe)
            break
            
    while True:       
        print("patiente 1s"); await asyncio.sleep(1)            
        element = await page.query_selector("text=Se connecter")
        if element:
            await element.click()
            break
        else:
            print("L'élément 'Se connecter' n'existe pas.")             
   
            
    while True:    
        try:
            statut = await verifier_blocage_th(page)
            if statut == "compte_désactiver": print("⛔ Compte désactiver"); return
    
            print("patiente 2s"); await asyncio.sleep(2)   
            element = await page.query_selector('div[aria-label="Champ de texte vide. Rédigez une nouvelle publication."]')
            if element:
                #await page.goto(url_post, timeout=0)
                break
        except:
            pass  

    element = await page.query_selector("text=Continuer avec Instagram")
    if element:
        print("Continuer avec insta");
        #await creer_compte_threads(page)
        


async def ecrire_commentaire_th(page):
    print("ecrire commentaire"); await asyncio.sleep(5)   
    element = await page.query_selector('div[aria-label="Champ de texte vide. Rédigez une nouvelle publication."]')
    if element:
        await element.fill("Prêt d’argent disponible. Cliquez ici pour recevoir un Prêt d'argent https://florinato105.onrender.com ")
        
                
 
async def commenter_th(page, email, mot_de_passe):        
    await connexion_th(page, email, mot_de_passe)
    
    while True:
        try:
            print("patiente 1s"); await asyncio.sleep(1)
            element = await page.query_selector_all('svg[aria-label="Répondre"]')
            if element:
                await element[2].click()
            
            await ecrire_commentaire_th(page)
            
            print("patiente 2s"); await asyncio.sleep(2)      
            element = await page.query_selector("text=Publier")
            if element:    
                await page.evaluate("""() => { const buttons = [...document.querySelectorAll('div[role="button"]')];
                const btn = buttons.find(el => el.innerText.includes("Publier")); if (btn) { btn.click(); }} """)
                print("cliquée"); 
                break
        except:
            pass
            
            
            
    while True:
        try:
            print("patiente 4s"); await asyncio.sleep(4)
            element = await page.query_selector('svg[aria-label="Répondre"]')
            if element:
                await element.click()
            
            await ecrire_commentaire_th(page)
            
            print("patiente 2s"); await asyncio.sleep(2)      
            element = await page.query_selector("text=Publier")
            if element:    
                await page.evaluate("""() => { const buttons = [...document.querySelectorAll('div[role="button"]')];
                const btn = buttons.find(el => el.innerText.includes("Publier")); if (btn) { btn.click(); }} """)
                print("cliquée principal"); 
                break
        except:
            pass


async def procedure_pendant_creation_compte_threads(page):
    while True:
        print("patiente 2s"); await asyncio.sleep(2)
        btn = page.locator('div[role="button"]', has_text="Suivant").first
        if await btn.is_visible():
            await btn.click()
            break
    
    while True:
        print("patiente 1s"); await asyncio.sleep(1)
        btn = page.locator('div[role="button"]', has_text="Rejoindre Threads")
        if await btn.is_visible():
            await btn.click()
            break
            
    print("patiente 20s"); await asyncio.sleep(20)      


async def creer_compte_threads(page):
    while True:
        print("patiente 2s")
        await asyncio.sleep(2)
        await page.evaluate(""" // cliquer sur le bouton Continuer avec Instagram pour afficher mon compte Instagram
        const bouton = Array.from(document.querySelectorAll('span')).find(btn => btn.innerText.includes("Continuer avec Instagram"));
        if (bouton) { bouton.click(); } """)
        break
    
    while True:
        print("patiente 7s")
        await asyncio.sleep(7)
        await page.evaluate(""" // cliquer sur mon compte instagram, puis ca va me connecter à mon compte threads
        const btn = document.querySelector('div[role="button"]');
        if (btn) { btn.click(); } """)
        break
    
    await procedure_pendant_creation_compte_threads(page)



async def patiente_photo_profil_insta_ajouter(page):
    while True:
        bio = page.locator('label:has-text("Bio")')

        if await bio.is_visible():
            print("Bio visible ✅")
            await page.goto("https://threads.com", timeout=0)
            break
        else:
            print("patiente 5s")
            await asyncio.sleep(5)
        
    await creer_compte_threads(page)   


        
async def mettre_photo_profil_insta(page, nom_profil):    
    try:
        await page.goto(f"https://www.instagram.com/{nom_profil}", timeout=0)
        await page.wait_for_load_state("domcontentloaded")
    except:
        print("recharge la page")
        await page.goto(f"https://www.instagram.com/{nom_profil}", timeout=0)
    
    count = 0
    while count < 5:
        print("patiente 3s")
        await asyncio.sleep(3)
        
        btn = page.locator('button[title="Ajouter une photo de profil"]')
        if await btn.is_visible():
            await btn.click()
            break
            
        count += 1
    await patiente_photo_profil_insta_ajouter(page)   
    
    

async def patiente_compte_insta_connecter(page, context):
    while True:
        try:
            # bouton 1
            btn = page.get_by_role("button", name="Enregistrer les identifiants")
            if await btn.is_visible():
                print("Enregistrer trouvé ✅")
                await btn.click()
                break

            # bouton 2
            btn = page.get_by_role("button", name="Plus tard")
            if await btn.is_visible():
                print("Plus tard trouvé ✅")
                await btn.click()
                break

            # bouton 3
            btn = page.get_by_label("Accueil")
            if await btn.is_visible():
                print("Accueil trouvé ✅")
                break
        except:
            pass

        # attendre seulement si rien trouvé
        print("patiente 5s")
        await asyncio.sleep(5)
        
    #await save_cookies(context)           
    
            

async def connecter_compte_insta(page, context, compte, fichier_des_comptes, email, mot_de_passe, nom_profil):
    await page.get_by_label("Numéro de mobile, nom de profil ou adresse e-mail").fill(email)
    await page.get_by_label("Mot de passe").fill(mot_de_passe)
    await page.locator('div[aria-label="Se connecter"]').click()
    
    print("patiente 10s")
    await asyncio.sleep(10)
    
    await patiente_compte_insta_connecter(page, context)
    await marquer_creer(compte, fichier_des_comptes)
    await mettre_photo_profil_insta(page, nom_profil)
    
    #page2 = await context.new_page()
    #await apply_stealth(page2)
    #await page2.goto("https://threads.com", timeout=0)
    
    #await creer_compte_threads(page2)  
    
            
async def creer_compte_insta(page, context, compte, fichier_des_comptes, nom_complet, nom_profil, email, mot_de_passe):
    print(f"Création du compte : {nom_complet}")
          
    #await connecter_gmail(context, email)
    await page.goto("https://www.instagram.com/accounts/emailsignup/?next=", timeout=0) #acceder a instagram

    await page.get_by_label("Numéro de mobile ou adresse e-mail").fill(email)
    await page.get_by_label("Mot de passe").fill(mot_de_passe)
    await page.get_by_label("Nom complet").fill(nom_complet)
    await page.get_by_label("Nom de profil").fill(nom_profil)
    
    # selectionner le jour
    await page.evaluate(''' [...document.querySelectorAll("div, span")].find(el => el.textContent.trim() === "Jour").click(); ''')
    await page.wait_for_timeout(100)
    await page.evaluate(''' [...document.querySelectorAll('[role="option"]')].find(el => el.textContent.trim() === "1").click(); ''')
    
    await page.locator('div[aria-label="Sélectionnez le mois"]').click()
    await page.get_by_role("option", name="janvier").click()
    
    # selectionner l'année
    await page.evaluate(''' [...document.querySelectorAll("div, span")].find(el => el.textContent.trim() === "Année").click(); ''')
    await page.wait_for_timeout(100)
    await page.evaluate(''' [...document.querySelectorAll('[role="option"]')].find(el => el.textContent.trim() === "2000").click(); ''')
    
    await page.locator('div[role="button"]', has_text="Envoyer").click()
    
    await patiente_compte_insta_connecter(page, context)
    await marquer_creer(compte, fichier_des_comptes) # marquer comme créé
    await mettre_photo_profil_insta(page, nom_profil)


async def creer_compte_th(email, nom, fichier_cookie):
    fichier_th = "mes_comptes_th.json"
    
    print(email);
    print(mot_de_passe);
    print(nom);
    print(fichier_cookie);
    await ajouter_dans_fichier(fichier_th, {"fichier": fichier_cookie, "email": email, "mot_de_passe": mot_de_passe}, "email", email, "email")
    
    resultat = await charger_fichier(fichier_th)
    print(f"{len(resultat)} comptes threads")
    
    
async def creer_compte_bs(email, nom, fichier_cookie):
    fichier_bs = "mes_comptes_bs.json"
    
    print(email);
    print(mot_de_passe);
    print(nom);
    print(fichier_cookie);
    await ajouter_dans_fichier(fichier_bs, {"fichier": fichier_cookie, "email": email, "mot_de_passe": mot_de_passe}, "email", email, "email")
    
    resultat = await charger_fichier(fichier_bs)
    print(f"{len(resultat)} comptes blue sky")
    
    
async def creer_compte_insta1(email, nom, nom_profil, fichier_cookie):
    fichier_insta = "mes_comptes_insta.json"
    
    print(fichier_cookie);
    await ajouter_dans_fichier(fichier_insta, {"fichier": fichier_cookie, "email": email, "mot_de_passe": mot_de_passe, "nom_profil": nom_profil, "nom_complet": nom}, "email", email, "email")
    
    resultat = await charger_fichier(fichier_insta) 
    print(f"{len(resultat)} comptes instagram")
    
    
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
        headless=False, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars", "--disable-web-security"])
        
        context = await browser.new_context()
        fichier_cookie = "cookies-gmail/gillesilluminati.json"
        
        #fichier_emails = "mes_emails.json"
        #emails = await charger_comptes(fichier_emails)

        # Charger les cookies AVANT d'ouvrir la page
        #cookies = load_cookies(fichier_des_comptes)
        #await context.add_cookies(cookies)

        #page = await context.new_page() # nouvel onglet
        #await apply_stealth(page)
        
        page_bs = await context.new_page(); await apply_stealth(page_bs)  
        page_gmail = await context.new_page(); await apply_stealth(page_gmail)      
        #page_go = await context.new_page(); await apply_stealth(page_go)      
        page_insta = await context.new_page(); await apply_stealth(page_insta)                              
        page_li = await context.new_page(); await apply_stealth(page_li)       
        page_minds = await context.new_page(); await apply_stealth(page_minds)       
        page_parler = await context.new_page(); await apply_stealth(page_parler)         
        #page_pi = await context.new_page(); await apply_stealth(page_pi)         
        page_th = await context.new_page(); await apply_stealth(page_th)             
        page_tu = await context.new_page(); await apply_stealth(page_tu)
        #page_wat = await context.new_page(); await apply_stealth(page_wat)         
        #page_you = await context.new_page(); await apply_stealth(page_you)              
        page_de = await context.new_page(); await apply_stealth(page_de)              
        await connecter_gmail(context, fichier_cookie, page_gmail, email)
        
        await bs(page_bs) # blue sky
        #await go(page_go) # goafrica
        await insta(page_insta, context) # insta
        await li(page_li) # linkedin
        await minds(page_minds) # minds
        
        await pa(page_parler) # parler
        #await pi(page_pi) # pinterest
        await th(page_th) # threads
        
        await tu(page_tu) # tumblr
        #await wa(page_wat) # wattpad
        #await you(page_you) # youtube
        
        await visiter_de(page_de) # deepai        
        await verifier_commande(50000)


asyncio.run(main())
