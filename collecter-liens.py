import json, asyncio, msvcrt, time, unicodedata
from playwright.async_api import async_playwright
from itertools import cycle
from outils_playwright import (connecter_gmail, sauvegarder_cookies, charger_cookies, sauvegarder_fichier, charger_fichier, charger_fichier_d, ajouter_dans_fichier,
mettre_a_jour, post_recent)



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


async def basculer_sur_le_compte(page):
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
        #element = await page.query_selector("text=Richesse avec SATAN")
        #if not element:
        #    await page.goto(url_page, timeout=0)
            
    else:
        print("Connecté sur le compte")
    
    
    
async def compter_commentaire(page, nom, url):   
    #print("patiente 5s"); await asyncio.sleep(5);
    
    temps_debut = time.monotonic()  # Enregistre le temps de début
    temps = 5
    
    while True:
        # Vérifie si le temps écoulé dépasse 10 secondes
        temps_ecouler = time.monotonic() - temps_debut
        if temps_ecouler > temps:
            print("Temps écoulé, arrêt")
            break
            
        btn = page.locator('div[role="button"]:has-text("Répondre")')
        if await btn.count() > 0:  
            await page.evaluate("""
            const buttons = document.querySelectorAll('div[aria-label="J’aime"]');
            for (let i = 0; i < Math.min(20, buttons.length); i++) {
              buttons[i].scrollIntoView({ behavior: "smooth", block: "center" });
            } """)
        
            count = await btn.count()
            print("Nombre de boutons Répondre :", count) 

            if count > 10:
                print("arrêt → Plus de 10 commentaires")
                
                #print("+ Pas encore liké"); 
                #page_active = await charger_fichier("page_active.json") #on sauvegarde les pages (Pas encore liker), qui ont plus de 5 commentaires 
                #page_active.append({ "name": name, "url": url_page })
                #await sauvegarder_sur_meme_ligne("page_active.json", page_active)
                
                
                await ajouter_dans_fichier("page_active2.json", { "page_active": url, "nom": nom }, "page_active", url)
                
                if "Compte vérifié" in nom:
                    print("✅ Compte vérifié")
                else:
                    print("Non vérifié")
                    await email(page, nom, url)
                    await message(page, nom, url)
                    
                break
    
        
        
async def nom_page(page, url):
    name = await page.locator("h1").first.text_content() # recuperer nom_page
    name = name.strip() if name else None
    await ajouter_dans_fichier("pages_collecter.json", {"page": url, "nom": name}, "page", url) # sauvegarder la page trouvé
    print("nom_page : ", name); return name
            
            
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
    
    await mettre_a_jour("pages_collecter.json", {"verfierEmail": 1}, "page", url)
    
    
async def message(page, nom, url):
    message_btn = await page.query_selector('div[aria-label="Message"]') # verifier si ya le btn message sur la page
    if message_btn:
        print("📩 message disponible")
        await ajouter_dans_fichier("page_messages_collecter.json", {"message": url, "nom": nom}, "message", url)
    else:
        print("❌ pas de message")
        


async def recuperer_lien(page, context):
    debut = time.monotonic()
    seen = set()
    
    blacklist = [ "/posts/", "/videos/", "/groups/", "sharer", "login", "privacy", "/photo/", "/61", "/pages", "/hashtag", "afad/", "groupslanding/",
        "notifications", "ad_campaign", "/professional_dashboard", "/reel", "l.facebook.com", "/onthisday", "/saved", "/ad_center", "/permalink.php", "/latest",
        "/friends_likes", "/photos", "/about", "/mentions", "/followers", "following"
    ]

    while True:
        try:
            if time.monotonic() - debut > 60: print("⏹️ Fin des 1 minutes"); break # stop après 3 minutes  
            
            links = await page.query_selector_all('[data-ad-rendering-role="profile_name"] a[href]')
            print(f"Trouvé {len(links)} liens")

            for link in links:
                url = await link.get_attribute("href")
                
                if "profile.php" in url:
                    url = url.split("&")[0]
                else:
                    url = url.split("?")[0]
                
                
                if not url: continue 
                if url in seen: continue # Skip déjà vus            
                
                if "-" in url or "%" in url: continue
                if any(x in url for x in blacklist): continue # Skip blacklist
                
                contenu = await charger_fichier("pages_collecter.json") or []
                
                url_existe_deja = False 
                for p in contenu: # verifier si url existe deja dans db
                    if p.get("page") == url: 
                        print("url existe déjà, non enregistrer"); 
                        url_existe_deja = True; 
                        break 
                
                if url_existe_deja: continue  # si url_existe_deja=True, on passe à l'url suivante

                seen.add(url)
                print("Ouverture :", url)
                
                try:
                    new_page = await context.new_page()
                    await new_page.goto(url)
                    print("patiente 2s"); await asyncio.sleep(2)
                    
                    
                    btn_ami = await new_page.query_selector('a[href*="/friends"]')
                    if not btn_ami:
                        nom = await nom_page(new_page, url);
                        await post_recent(new_page)
                        await compter_commentaire(new_page, nom, url)
                        print("patiente 1s"); await asyncio.sleep(1)
                        
                    await new_page.close()
                except Exception as e:
                    print("cc.."); #print("❌erreur :"); print(e)
                    await new_page.close()

            # Scroll pour charger plus de contenu 
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            print("patiente 1s"); await asyncio.sleep(1)
            
        except Exception as e:
            print("..erreur"); print(e)
        
        
async def verifier_dernier_mot():
    fichier_mot_debut = "mot_debut.json" # dernier_mot_cle.json
    mot_debut = (await charger_fichier_d(fichier_mot_debut)).get("mot_cle")
    
    fichier_mot = "mot_cles.json"
    mots = await charger_fichier(fichier_mot) # Charger la liste de mots cles
    
    if mot_debut:
        # Si un dernier mot est enregistré, trouver son index
        for mot in mots:
            if mot == mot_debut:
                mot_debut = mot
                break
                
    return mots, mot_debut, fichier_mot_debut


async def collecter_liens(page, context):
    await page.goto("https://fb.com", timeout=0)
    await basculer_sur_le_compte(page)
    mots, mot_debut, fichier_mot_debut = await verifier_dernier_mot()
    print(f"mot_debut : {mot_debut}")
    
    
    while True:
        start_index = 0
        if mot_debut:
            if mot_debut in mots:
                start_index = mots.index(mot_debut) # Trouver l'index du mot de début
                
        for i in range(start_index, len(mots)):
            mot = mots[i]
            mot_suivant = mots[i+1]
            print(f"🔍 Recherche : {mot}")
        
            while True:
                try:
                    print("patiente 1s"); await asyncio.sleep(1)
                    input_box = page.get_by_placeholder("Rechercher sur Facebook")
                    if await input_box.count() > 0:                 
                        await input_box.fill(mot)
                        await input_box.press("Enter")

                    print("patiente 2s"); await asyncio.sleep(2)
                    btn = page.get_by_label("Publications récentes")
                    if await btn.count() > 0:                                               
                        await btn.click()
                        break
                except Exception as e:
                    print("..erreur"); print(e)
        
            await recuperer_lien(page, context)
            await sauvegarder_fichier(fichier_mot_debut, { "mot_cle": mot_suivant })
    
    
    
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

        fichier_des_comptes = "comptes-fb.json"
        comptes = await charger_comptes(fichier_des_comptes)
        comptes = [c for c in comptes if c.get("message") == "1"] # message_speciale
        comptes = [c for c in comptes if not str(c.get("fichier", "")).strip().startswith("-")] # ignorer les comptes qui commencent par -
        
        count = 0
        while count < 2: 
            for compte in comptes:
                #fichier_cookie = compte["fichier"]
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("id_inchangeable")

                
                print("✅", nomDeMonCompte); #print(name); print(url_page);
                
                context = await browser.new_context() #nouveau contexte pour chaque compte
                
                cookies = charger_cookies(fichier_cookie) # Charger les cookies AVANT d'ouvrir la page
                await context.add_cookies(cookies)

                page = await context.new_page()
                await apply_stealth(page)
                
                await collecter_liens(page, context)
                
                #await sauvegarder_fichier(fichier_derniere_page, {"name": name}) # ✅ sauvegarde de la dernière page
                #await sauvegarder_cookies(context, fichier_cookie)
                
                print("patiente 10000s"); await asyncio.sleep(10000)
                await context.close()

            count += 1

if __name__ == "__main__":
    asyncio.run(main())
