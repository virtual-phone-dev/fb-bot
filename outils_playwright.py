import json, os, asyncio, random, sqlite3, msvcrt, time, unicodedata
from datetime import datetime

mot_de_passe_gmail = "diel2019"
email_recuperation = "kilendodingha@gmail.com"

mots_inutiles = ["fédération", "gendarmerie", "armed", "armées", "forces", "police", "commission", "nationale", "commissariat", "commune", "ministère", "primature"]

domaines_autoriser = ("gmail.com", "yahoo.com", "yahoo.fr", "yahoo.co.uk", "yahoo.ca", "outlook.com", "outlook.fr", "hotmail.com", "live.fr", "orange.fr", "free.fr", 
"sfr.fr", "laposte.net", "wanadoo.fr", "icloud.com", "me.com", "mac.com", "protonmail.com", "laposte.net")
    


async def appliquer_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] }); """)


async def apply_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] }); """)


# en cas d'erreur, jutiliserai des parties de ce code
async def nom_page(page, url):
    while True:
        try:
            print("patiente 5s"); await asyncio.sleep(5)
            name = await page.locator("h1").first.text_content() # recuperer nom_page
            name = name.strip() if name else None
            print(" ss")
            await ajouter_dans_fichier("pages_collecter.json", {"page": url, "nom": name}, "page", url) # sauvegarder la page trouvé
            print("tt ")
            print("nom_page : ", name); return name
        except Exception as e:
            print("..erreur"); print(e)
            



async def clic_div_aria_label_role_button(page, textes, cliquer=False):
    #while True:
    print("patiente 1s"); await asyncio.sleep(1)
    for t in textes:
                
        btn = page.locator(f'div[aria-label="{t}"][role="button"]').first
        if await btn.count() > 0:    
            if cliquer:
                await btn.click()
            return btn
    return None
    


async def span_has_text(page, textes, cliquer=False):
    try:
        for t in textes:
            
            btn = page.locator(f'span:has-text("{t}")')        
            if await btn.count() > 0:  
                
                if cliquer: await btn.click()
                return btn
        return None
    except:
        pass
        

        
        
# VERIFIER COMMANDE CONSOLE
async def verifier_commande(page, duree_pause):
    print("Écrivez..")
    secondes = duree_pause * 1 # duree_pause x nbre_secondes
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
    #print("suivant automatique")
    
    
async def verifier_blocage2(context, page, fichier):
    while True:
        try:
            element = await page.query_selector("text=Continuer")
            if element:
                await element.click()

            element = await page.query_selector("text=Ignorer")
            if element:
                await element.click()
                
            input_box = page.get_by_placeholder("Rechercher sur Facebook")
            if await input_box.count() > 0: 
                await sauvegarder_cookies(context, fichier);
                break
                
            print("patiente 2s"); await asyncio.sleep(2)
        except:
            pass
    
        
        
async def verifier_blocage(page):
    print("patiente 3s"); await asyncio.sleep(3)
    btn = await page.query_selector("text=confirmez que vous êtes une personne réelle afin d’utiliser votre compte")
    if btn:
        #print("bloqué selfie video")
        return "bloquer_selfie_video"
    
    
async def reparer_fb(page):
    btn = await page.query_selector("text=confirmez qu’il s’agit de votre compte pour le déverrouiller")
    if btn:
        print("bloqué - confirmez...")
        #print("patiente 2 minutes"); await asyncio.sleep(60*2)
        
        while True:
            print("patiente 2s"); await asyncio.sleep(2)
            btn = page.get_by_label("Votre profil")
            if await btn.count() > 0:
                return "connecté_déblocage_réussi"


    
async def nettoyer_texte(txt): #ce code permet pour que, Église, eglise, puisse marcher
    txt = txt.lower().strip()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    
    return txt


def nettoyer_texte2(texte: str, supprimer: list[str] = None) -> str:
    # Nettoie un texte : supprime mots indésirables + espaces multiples
    if not texte: return ""
    
    for mot in (supprimer or []):
        texte = texte.replace(mot, "")
    
    return re.sub(r'\s+', ' ', texte).strip()
    
    

async def verifier_date_recontacte(mail):
    if "recontacter" not in mail: return True 
    
    try:
        date_recontacte = datetime.strptime(mail["recontacter"], format_date)
    except:
        return True
        
    return datetime.now() >= date_recontacte
    


async def creer_context(browser, fichier):
    cookie_file = f"cookies-bs/{fichier}.json"
    
    if os.path.exists(cookie_file):
        contexte = await browser.new_context(storage_state=cookie_file)
    else:
        # Créer un contexte sans cookies (première connexion)
        contexte = await browser.new_context()
    
    return contexte
    
    
async def verifier_nouveau_element(fichier1, fichier2, cle_db):
    data = await charger_fichier(fichier1) # Charger le fichier emails_collecter.json et emails_collecter2.json
    data2 = await charger_fichier(fichier2)
    
    #emails_collecter = [c for c in data if not c["fichier"].startswith("-")] # fichier3_filtrer
    #emails_collecter2 = [c for c in data2 if not c["fichier"].startswith("-")]
    
    emails_collecter = [c for c in data if not str(c.get("fichier", "")).startswith("-")]
    emails_collecter2 = [c for c in data2 if not str(c.get("fichier", "")).startswith("-")]
    
    nouveaux_emails = []
    for element in emails_collecter: # Vérifier si de nouveaux emails sont dans emails_collecter.json
        if not any(element.get(cle_db) == e.get(cle_db) for e in emails_collecter2): #on verifie si element est deja dans le 2e fichier - emails_collecter2
            nouveaux_emails.append(element) #any sert a lire le resultat
    
    if nouveaux_emails: # Si on a de nouveaux emails, les ajouter à emails_collecter2
        emails_collecter2.extend(nouveaux_emails)
        await sauvegarder_sur_meme_ligne(fichier2, emails_collecter2) # Sauvegarder la nouvelle liste dans emails_collecter2.json

    return emails_collecter2       
        
        
        
async def acceder_page(page):
    textes = ["Richesse avec SATAN", "Secte de SATAN"]

    while True:
        await asyncio.sleep(1)

        for t in textes:
            btn = await page.query_selector(f"text={t}")
            if btn:
                await btn.click()  #print(f"trouvé et cliqué : {t}")
                await asyncio.sleep(1)
                return       
        
        
async def basculer_sur_le_compte(page, url_page):
    btn = page.locator('a[aria-label="Espace Pubs"][role="link"]').first
    if await btn.count() > 0:  
        print("Connecté sur la page") #print("Espace Pubs trouvé")
      
        while True:
            print("patiente 2s"); await asyncio.sleep(2)
            btn = page.get_by_label("Votre profil")
            if await btn.count() > 0:
                await page.evaluate("""
                const btn = document.querySelector('div[aria-label="Votre profil"]');
                if (btn) { btn.click(); } """)
                break
                
        while True:
            print("patiente 3s"); await asyncio.sleep(3)  
            btn = page.get_by_label("Basculer sur")
            if await btn.count() > 0:
                await page.evaluate("""
                const btn = document.querySelector('div[aria-label*="Basculer sur"]');
                if (btn) { btn.click(); } """)
                break
                
        print("patiente 5s"); await asyncio.sleep(5)  
        element = await page.query_selector("text=Richesse avec SATAN")
        if not element:
            await page.goto(url_page, timeout=0)
            
    else:
        print("Connecté sur le compte")
    
    
    
async def basculer_sur_la_page(page):
    
    btn = page.locator('a[aria-label="Espace Pubs"][role="link"]').first
    if await btn.count() > 0:  
        #print("Espace Pubs trouvé")
        print("Connecté sur la page")
        
    else:    
        
        while True:
            print("patiente 2s"); await asyncio.sleep(2)
            btn = page.get_by_label("Votre profil")
            if await btn.count() > 0:
                await page.evaluate("""
                const btn = document.querySelector('div[aria-label="Votre profil"]');
                if (btn) { btn.click(); } """)
                break
                
        while True:
            print("patiente 3s"); await asyncio.sleep(3)  
            btn = page.get_by_label("Basculer sur")
            if await btn.count() > 0:
                await page.evaluate("""
                const btn = document.querySelector('div[aria-label*="Basculer sur"]');
                if (btn) { btn.click(); } """)
                break
                          
        while True:   
            try:
                print("patiente 5s"); await asyncio.sleep(5)
                btn = await page.query_selector("text=Quoi de neuf")
                if btn:
                    print("Connecté sur la page")
                    break
            except:
                pass
            
            
            
async def connecter_gmail(context, fichier_cookie, page, email):
    try:
        await page.goto("https://mail.google.com", timeout=0)
    except:
        await page.goto("https://mail.google.com", timeout=0)
    
    
    btn = page.locator('div[role="button"]:has-text("Nouveau message")')
    if await btn.count() > 0:
        return
    
    while True:
        btn = page.locator('text="Utiliser un autre compte"')
        if await btn.count() > 0:
            print("Déconnecter, aller sur la page de connexion")
            await btn.click()
            
        #print("patiente 1s"); await asyncio.sleep(1)
        #btn = await page.query_selector("text=Utiliser un autre compte")
        #if btn:
        #    print("Déconnecter, aller sur la page de connexion")
        #    await btn.click()
                    
        print("patiente 2s"); await asyncio.sleep(2)
        btn = page.get_by_label("Adresse e-mail ou téléphone")
        if await btn.count() > 0:
            await page.get_by_label("Adresse e-mail ou téléphone").fill(email)
            #await btn.click()
            await page.get_by_role("button", name="Suivant").click()
            #break
    
    #while True:
        print("patiente 4s"); await asyncio.sleep(4)
        btn = page.get_by_label("Saisissez votre mot de passe")
        if await btn.count() > 0:
            await page.get_by_label("Saisissez votre mot de passe").fill(mot_de_passe_gmail)
            await page.get_by_role("button", name="Suivant").click()
            #break
        
        try:
            print("patiente 2s"); await asyncio.sleep(2);         
            element = page.locator('input[type="email"]')
            if await element.count() > 0:
                await element.fill(email_recuperation)    
        except:
            pass 
            
    #while True:    
        #print("patiente 1s"); await asyncio.sleep(1)
        try:
            print("patiente 2s a"); await asyncio.sleep(2); 
            textes = ["Enregistrer", "Save"]
            for t in textes:

                btn = page.get_by_label(f"{t}")
                if await btn.count() > 0:
                    await btn.click()
                    print("patiente 3s"); await asyncio.sleep(3); 
                    break
        except:
            pass 
            

        try:
            textes = ["Ignorer", "Skip"]
            for t in textes:
                
                btn = page.get_by_label(f"{t}")
                if await btn.count() > 0:
                    await btn.click()
                    break
        except:
            pass 
            

        try:
            btn = page.locator('div[role="link"]:has-text("Confirmer votre adresse e-mail de récupération")')
            if await btn.count() > 0:
                await btn.click()
        except:
            pass
            
    
        try:
            btn = page.get_by_label("Saisissez l'adresse e-mail de récupération")
            if await btn.count() > 0:
                await page.get_by_label("Saisissez l'adresse e-mail de récupération").fill("kilendodingha@gmail.com")
                await page.get_by_role("button", name="Suivant").click()
        except:
            pass
            
        
        try:
            btn = page.locator('span:has-text("Besoin d\'aide pour récupérer votre compte")')
            if await btn.count() > 0:
                await btn.click()
        except:
            pass


        try:
            btn = page.get_by_label("Saisissez votre dernier mot de passe")
            if await btn.count() > 0: 
                await page.get_by_label("Saisissez votre dernier mot de passe").fill(mot_de_passe_gmail)
                await page.get_by_role("button", name="Suivant").click()
        except:
            pass

        
        try:
            btn = page.get_by_label("Continuer")
            if await btn.count() > 0:
                await btn.click()
        except:
            pass
            

        try:
            textes = ["Nouveau message", "Compose"]
            trouver = False
            for texte in textes:
                
                btn = page.locator(f'div[role="button"]:has-text("{texte}")')
                if await btn.count() > 0:
                    trouver = True
                    await sauvegarder_cookies(context, fichier_cookie)
                    break
                    
            if trouver: break
        except Exception as e:
            print("..erreur"); print(e); pass
            
        
        element = await span_has_text(page, ["Impossible de vous connecter"])
        if element: print("Impossible_de_vous_connecter"); return "Impossible_de_vous_connecter"
        
            
        textes = [
        "Le serveur ne peut pas traiter la requête, car son format est incorrect. Nous vous recommandons de ne pas réessayer",
        "The server encountered a temporary error and could not complete your request."]
        for t in textes:
            try:
                await page.wait_for_load_state("networkidle")
                
                element = await page.evaluate("""() => { return [...document.querySelectorAll('main')].find(el => el.innerText.includes("Le serveur ne peut pas traiter la requête, car son format est incorrect. Nous vous recommandons de ne pas réessayer")); } """)        
                if element:
                    print("erreur_serveur_gmail"); return "erreur_serveur_gmail"
            except Exception as e:
                print("..erreur"); print(e); pass
        
        
async def post_recent(page):
    btn = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    if await btn.count() > 0:    
        await btn.click()
        print("patiente 2s"); await asyncio.sleep(2); 


def sauvegarder_json(fichier, data):
    with open(fichier,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Posts liker
def post_deja_liker(posts, lien):
    if not lien:
        return False

    return lien in posts
    
           
def ajouter_post(posts, fichier, lien):
    if lien not in posts:
        posts.append(lien)
        sauvegarder_json(fichier, posts)
        
        
async def recuperer_texte_th(page, posts, fichier_posts):
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:        
        element = page.locator('[data-pressable-container="true"]').first
        texte = await element.inner_text()
        
        if texte:
            lignes = texte.split("\n")
            if len(lignes) >= 3:
                texte_post = lignes[2].strip()
            else:
                texte_post = ""

            identifiant_post = texte_post[:500]    
        
        # ICI on coupe à 500 caractères pour eviter les tres long texte dans mon fichier
        #identifiant_post = " ".join(texte.split())[:500] #print(f"Texte : {identifiant_post[:80]}")

        if posts and post_deja_liker(posts, identifiant_post): 
            print(f"Déjà liké"); return "deja_liker" # Vérification déjà liké
        
        # Sauvegarde texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post) #print("Texte sauvegardé")
    except:
        pass #print("Impossible de récupérer le texte :", e)



async def recuperer_texte_bs(page, posts, fichier_posts):
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:        
        element = page.locator('div[data-testid="contentHider-post"]').first
        texte = await element.text_content()
        
        # ICI on coupe à 500 caractères pour eviter les tres long texte dans mon fichier
        identifiant_post = " ".join(texte.split())[:500] #print(f"Texte : {identifiant_post[:80]}")
        
        if posts and post_deja_liker(posts, identifiant_post): 
            print(f"Déjà liké"); return "deja_liker" # Vérification déjà liké

        # Sauvegarde texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post) #print("Texte sauvegardé")
    except:
        pass #print("Impossible de récupérer le texte :", e)
                       


#const h1 = document.querySelector('h1[dir="auto"]'); // ou 'h1' si tu veux le premier h1
#const text = h1.innerText; // ou h1.textContent
#console.log(text);

async def recuperer_texte_insta(page, posts, fichier_posts):
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:        
        element = page.locator('h1').first
        if await element.count() > 0:
            texte = await page.evaluate(""" () => {
            const h1s = document.querySelectorAll('h1[dir="auto"]');
            for (let i = 0; i < h1s.length; i++) {
                const text = h1s[i].innerText;
                if (text.includes(" ")) { console.log(text); return text; break; }
            } } """);
            
            
            #texte = await element.text_content()
            print(f"texte trouvé:", texte);
            
        # ICI on coupe à 500 caractères pour eviter les tres long texte dans mon fichier
        identifiant_post = " ".join(texte.split())[:500] #print(f"Texte : {identifiant_post[:80]}")
        if posts and post_deja_liker(posts, identifiant_post): 
            print(f"Déjà liké"); return "deja_liker" # Vérification déjà liké
        
        # Sauvegarde texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post) #print("Texte sauvegardé")
    except:
        pass #print("Impossible de récupérer le texte :", e)           
         
         
         
# Charger cookies
def charger_cookies(fichier):
    if not os.path.exists(fichier):
        return []

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            raw_cookies = data.get("cookies", [])
        elif isinstance(data, list):
            raw_cookies = data
        else:
            return []
    except:
        return []

    cookies = []
    for c in raw_cookies:
        if not isinstance(c, dict):
            continue

        cookies.append({
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "expires": c.get("expirationDate", -1),
        })
    return cookies
    
    
# Sauvegarder cookies
async def sauvegarder_cookies(contexte, fichier):    
    dossier = os.path.dirname(fichier) #créer le dossier si il n'existe pas
    if dossier:
        os.makedirs(dossier, exist_ok=True)

    state = await contexte.storage_state()
    
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

    print(f"cookies sauvegardés")
    
    

async def sauvegarder_sur_meme_ligne(fichier, data):
    with open(fichier, "w", encoding="utf-8") as f:
        f.write("[\n")
        for i, item in enumerate(data):
            json_line = json.dumps(item, ensure_ascii=False, separators=(', ', ':'))
            if i > 0:
                f.write(",\n")
            f.write(f"  {json_line}")
        f.write("\n]")
        
        
async def sauvegarder_fichier(fichier, data):
    dossier = os.path.dirname(fichier) #si jai besoin du dossier, et que ca existe pas, il va creer ca
    if dossier:
        os.makedirs(dossier, exist_ok=True)
        
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
           
        
async def charger_fichier(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []
        

async def charger_fichier_d(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


async def charger_fichier_t(fichier):
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return [ligne.strip() for ligne in f if ligne.strip()]  # strip pour ignorer les espaces, et les lignes saut de lignes
    except:
        return ""
        
        
def charger_posts(fichier):
    if not os.path.exists(fichier):
        return []
    with open(fichier, "r", encoding="utf-8") as f:
        return json.load(f)
        

async def ajouter_dans_fichier(fichier, data, cle_db, cle, trier=None):
    contenu = await charger_fichier(fichier) or [] # liste de contenus
    for p in contenu:
        if p.get(cle_db) == cle: print("existe déjà, non enregistrer"); return  
        
    contenu.append(data) # nouveau contenu, il ajoute le nouveau contenu dans la liste de contenus
    if trier:
        contenu.sort(key=lambda x: x.get(trier, "").lower()) # tri ALPHABÉTIQUE
        
    await sauvegarder_sur_meme_ligne(fichier, contenu)



async def mettre_a_jour(fichier, data, cle_db, cle):
    contenus = await charger_fichier(fichier)

    for p in contenus:
        #if p.get("page") == url:
        if p.get(cle_db) == cle:
            p.update(data)
            #p[champ] = valeur_champ
            #p["verfierEmail"] = 1
            break

    await sauvegarder_sur_meme_ligne(fichier, contenus)

    
# Ouvrir Facebook
async def ouvrir_facebook(contexte):
    page = await contexte.new_page()
    await appliquer_stealth(page)
    await page.goto("https://www.facebook.com",timeout=0)
    return page

# Ouvrir bs
async def ouvrir_bs(contexte):
    page = await contexte.new_page()
    await appliquer_stealth(page)
    await page.goto("https://bsky.app/",timeout=0)
    return page
    
    
# Pause en minutes
async def pause(minutes):
    await asyncio.sleep(minutes * 60)


# Injecter cookies
async def injecter_cookies(contexte, fichier):
    cookies = charger_cookies(fichier)
    await contexte.add_cookies(cookies)


# Créer contexte
async def creer_contexte(browser, cookie_file):
    contexte = await browser.new_context()
    await injecter_cookies(contexte,cookie_file)
    return contexte


    
async def creer_context2(browser, cookie_file):
    contexte = await browser.new_context(storage_state=cookie_file)
    contexte.set_default_timeout(180000)
    contexte.set_default_navigation_timeout(180000)
    return contexte
    
    
# Créer page
async def creer_page(contexte):
    page = await contexte.new_page()
    await appliquer_stealth(page)
    return page


# Aller vers URL
async def aller(page, url):
    await page.goto(url)
    # await page.wait_for_load_state("networkidle")


async def goto_with_domcontentloaded(page, url):
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")
    
    
# Pause aléatoire en secondes
async def pause_random(min, max):
    import random
    await asyncio.sleep(random.uniform(min,max))


            
def sauvegarder_json(fichier, data):
    with open(fichier,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Posts commentés
def post_deja_commente(posts, lien):
    if not lien:
        return False

    return lien in posts
        
    
def ajouter_post(posts, fichier, lien):
    if lien not in posts:
        posts.append(lien)
        sauvegarder_json(fichier, posts)
        
        

def ajouter_profil(lienAmis, nomAmis, monCompte):
    conn = sqlite3.connect("profils.db"); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO listeAmis(lienAmis, nomAmis, monCompte) VALUES(?, ?, ?)", (lienAmis, nomAmis, monCompte))
    conn.commit()


async def collecter_liens(page, nomFichierCompte):
    liens_vus = set()

    while True:
        profils = await page.evaluate("""() => { 
        const links = document.querySelectorAll('.x78zum5.x1q0g3np.x1a02dak.x1qughib a'); 
        
        const result = []; 
        links.forEach(link => { 
            const span = link.querySelector('span'); // sélectionner le span à l’intérieur du lien
            
            if(!span) return; // Vérifie si le span existe
            const href = link.href; 
            const nom = span.textContent.trim(); 
            
            if(nom === '') return; // Ignorer si le nom est vide
            if(href.endsWith('friends_mutual')) return; // Ignorer si l'URL se termine par 'friends_mutual'
            
            // Ignorer pages, events, groups
            if(href.includes('/pages/')) return;
            if(href.includes('/events/')) return;
            if(href.includes('/groups/')) return;
        
            result.push({lienAmis: href, nomAmis: nom}); // Obtenir le lien et le nom
        }); 
        return result; }""")
        nouveaux = 0

        for profil in profils:
            url = profil["lienAmis"]; nom = profil["nomAmis"]
            if url not in liens_vus:
                liens_vus.add(url); ajouter_profil(url, nom, nomFichierCompte); nouveaux += 1
                print("lien ajouté :", nom, url); 
                
        print("monCompte :", nomFichierCompte)
        print("nouveaux liens :", nouveaux)
        await page.mouse.wheel(0, 5000)
        await asyncio.sleep(3)
        
        

async def envoyer_message(page, MESSAGES, page_name=None, page_url=None, cookie_file=None):

    await page.evaluate("""
    const messageButton = document.querySelector('div[aria-label="Message"]'); // cliquer sur le bouton Message, une popup s'ouvre alors , pour ecrire le message
    if (messageButton) { messageButton.click(); }
    """)
    await asyncio.sleep(random.uniform(5, 7))

    # detection limite facebook
    limite = await page.locator("span:has-text('Vous avez atteint la limite d’invitations par message')").count()
    if limite > 0: print("Limite: ", cookie_file); return "limite"

    message_box = page.locator('div[aria-label="Écrire un message"]').first
    message = random.choice(MESSAGES)
    await message_box.fill(message)
    
    await asyncio.sleep(random.uniform(2, 4))
    await page.keyboard.press("Enter")

    print("Message envoyé :", message); print(cookie_file); print(page_name); print(page_url)
    await asyncio.sleep(random.uniform(15, 20))
    return "ok"   
    
      
async def envoyer_commentaire_bs(page, posts=None, fichier_posts=None, page_name=None, page_url=None, cookie_file=None):
    identifiant_post = None
    commentaire = "Salut, je suis développeur, si tu as envies de créer un réseau social ou une application mobile, je suis disponible."
    
    # attendre chargement posts
    try:
        await page.wait_for_selector('div[data-testid="contentHider-post"]', timeout=60000)
    except:
        print("Les posts ne se chargent pas"); return False

    # 🔹 trouver le premier post
    post_locator = page.locator('div[data-testid="contentHider-post"]').first
    count_post = await post_locator.count()

    if count_post == 0: print("❌ Aucun post trouvé"); return False

    # 🔹 récupérer texte du post
    try:
        texte = await post_locator.text_content() or ""
        identifiant_post = " ".join(texte.split())[:500]
        print("Texte :", identifiant_post[:80])

        # vérifier déjà commenté
        if posts and post_deja_commente(posts, identifiant_post): print("Déjà commenté"); return True

        # sauvegarder texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post)

    except Exception as e:
        print("Erreur récupération texte :", e)
        return False


    # 🔹 cliquer sur le post
    await page.evaluate("""
    const posts = document.querySelectorAll('div[data-testid="contentHider-post"]');
    if (posts.length > 0) { posts[0].click(); } """)
    await asyncio.sleep(random.uniform(5, 7))


    # 🔹 cliquer sur le bouton Repondre ou rédiger réponse
    await page.evaluate("""
    const buttonRédiger = document.querySelector('button[aria-label="Rédiger une réponse"]');
    if (buttonRédiger) { buttonRédiger.click(); } """)
    await asyncio.sleep(random.uniform(5, 7))
    
    # attendre apparition zone texte
    await page.wait_for_selector("div[role='textbox']", timeout=10000)

    # écrire le commentaire
    comment_box = page.locator("div[role='textbox']").first
    await comment_box.fill(commentaire)
    await asyncio.sleep(random.uniform(4, 6))

    # publier
    await page.evaluate("""
    const boutonPublier = document.querySelector('button[aria-label="Publier la réponse"]');
    if (boutonPublier) { boutonPublier.click(); } """)
    
    print("✅ Commentaire envoyé :", comment)
    print(cookie_file)
    print(page_name)
    print(page_url)
        
    await asyncio.sleep(random.uniform(10, 15))
    return True


        
async def envoyer_commentaire(page, COMMENTS, posts=None, fichier_posts=None, page_name=None, page_url=None, cookie_file=None, commented_posts=None, context=None):
    identifiant_post=None; post_link=None

    # 🔹 Vérification indisponibilité
    try:
        indisponible = await page.evaluate('''() => { return document.body.innerText.includes("Ce contenu n’est pas disponible pour le moment") }''')
        if indisponible:
            print("❌ Page indisponible, fermeture du navigateur")
            if context:
                await page.close()
                await context.close()
            return False
    except:
        pass
        

    # CHOIX DU PREMIER POST
    post_comment_button = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    count_post_comment_button = await post_comment_button.count()

    if count_post_comment_button > 0:        
        source_post = post_comment_button
    else:
        source_post = page.locator('[role="article"]').nth(0)

    
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:        
        post_element = page.locator('[data-ad-rendering-role="story_message"]').first
        texte = await post_element.text_content()
        
        # 🔥 ICI on coupe à 500 caractères
        identifiant_post = " ".join(texte.split())[:500]
        print(f"Texte : {identifiant_post[:80]}")

        # Vérification déjà commenté
        if posts and post_deja_commente(posts, identifiant_post):
            #print(f"Déjà commenté")

            if context:
                await page.close()
                await context.close()

            return True

        # Sauvegarde texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post)
            #print("Texte sauvegardé")

    except Exception as e:
        print("Impossible de récupérer le texte :", e)
        return False
        
        
    # RÉCUPÉRATION LIEN
    link_locator = source_post.locator("a[href*='/posts/'], a[href*='/videos/']")
    count_link = await link_locator.count()

    if count_link > 0:
        post_link = await link_locator.first.get_attribute("href")
        print("lien trouvé :", post_link)
    else:
        post_link = None
   

    # CAS 1
    if count_post_comment_button > 0:
        await post_comment_button.click()
        print("Attente apparition zone commentaire")
        await asyncio.sleep(random.uniform(5, 8))

        # CLIQUER SUR "RÉPONDRE"
        await page.evaluate(""" 
        const btn = Array.from(document.querySelectorAll('button, [role="button"]'))
          .find(b => b.innerText.trim() === 'Répondre');
        if (btn) btn.click(); 
        """);
        
        await asyncio.sleep(random.uniform(5, 8))

        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)
        await asyncio.sleep(random.uniform(4, 6))
        await page.keyboard.press("Enter")
        
        print(f"✅ Commentaire envoyé : {comment}")
        print(f"{page_name}")
        print(f"{page_url}")     
        print(f"{cookie_file}")
        
        await asyncio.sleep(random.uniform(20, 25))
        return True
        

    # CAS 2
    if post_link:
        # CLIQUER SUR "RÉPONDRE"
        await page.evaluate(""" 
        const btn = Array.from(document.querySelectorAll('button, [role="button"]'))
          .find(b => b.innerText.trim() === 'Répondre');
        if (btn) btn.click(); 
        """);

        await asyncio.sleep(random.uniform(4, 6))
    
        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)
        await page.keyboard.press("Enter")
        
        print("Cas 2")
        print(f"✅ Commentaire envoyé : {comment}")
        print(f"{page_name}")
        print(f"{page_url}")
        print(f"{cookie_file}")
        
        await asyncio.sleep(random.uniform(20, 25))
        return True


    # CAS 3
    print("❌ Aucun selecteur commentaire trouvé (Cas 3 à ajouter)")
    return False
    
    
