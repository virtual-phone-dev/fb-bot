import json, asyncio, msvcrt, time, unicodedata
from playwright.async_api import async_playwright
from itertools import cycle
from outils_playwright import (connecter_gmail, clic_div_aria_label_role_button, sauvegarder_cookies, charger_cookies, sauvegarder_fichier, charger_fichier, 
charger_fichier_d, ajouter_dans_fichier, mettre_a_jour, post_recent, verifier_blocage2, nettoyer_texte, mots_inutiles, domaines_autoriser, clic_div_aria_label_role_button,
query_selector_text, compter_followers_fb, verifier_nouveau_element, verifier_date_recontacte, verifier_commande)




#if (document.body.innerText.includes("Musique/groupe")) {
#	console.log("✅ trouvé");
#} else {
#	console.log("❌ non trouvé !");
#}



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
    
    nom_clean = await nettoyer_texte(nom)
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
                await ajouter_dans_fichier("page_active2.json", { "page_active": url, "nom": nom }, "page_active", url)
                
                if "Compte vérifié" in nom:
                    print("✅ Compte vérifié")
                else:
                    print("Non vérifié")
                    if not any(nom_compte in nom_clean for nom_compte in mots_inutiles): # si nom_compte nest pas dans mots_inutiles, alors tu l'enregistres
                        await email(page, nom, url)
                        await message(page, nom, url)
                    
                break
            else:
                if not any(nom_compte in nom_clean for nom_compte in mots_inutiles):
                    await email(page, nom, url)
                    await message(page, nom, url)
                    




        
        
async def nom_page(page, url):
    try: # recuperer nom_page
        name = await page.evaluate('''() => {
        const el = document.querySelector('span[dir="auto"] div[role="button"]');
        return el ? el.childNodes[0].textContent.trim() : null; }''')
        
        print("name aa", name)
    except Exception as e:
        print("pas de nom"); print(e)
                
        
    btn_follower = await page.evaluate("""() => { return [...document.querySelectorAll('span')].find(el => el.innerText.includes("Followers")); } """)
    if not btn_follower: 
        print("ami");
        await ajouter_dans_fichier("pages_collecter_artistes.json", {"nom": name, "url": url, "ami": 1}, "url", url) #lien du compte ami
    else:
        await ajouter_dans_fichier("pages_collecter_artistes.json", {"nom": name, "url": url}, "url", url)
        
                    
        statut = await query_selector_text(page, ["Artiste", "Musique/groupe", "Groupe", "Rappeur"])
        if statut: 
            
            follower = await compter_followers_fb(page)
            if follower is not None and follower < 10000:
                print("artiste trouvé"); 
                await ajouter_dans_fichier("pages_collecter_artistes.json", {"nom": name, "url": url}, "url", url) # sauvegarder la page trouvé
                await ajouter_dans_fichier("pages_collecter_artistes2.json", {"nom": name, "url": url}, "url", url) 
                
                
                numero = await numero_telephone(page);
                if numero: 
                    print("numéro trouvé"); 
                    await mettre_a_jour("pages_collecter_artistes2.json", {"telephone": numero}, "url", url)
                else:
                    print("pas de numero"); 
                    await mettre_a_jour("pages_collecter_artistes2.json", {"telephone": 0}, "url", url)
                    
            else:
                print("non trouvé")
        else:
            print("pas artiste"); 
            
        return name;
    
                        
                        
            
async def email(page, nom_page, url):           
    element = await page.query_selector('[href^="mailto:"]') # recuperer email

    email = None
    if element:
        href = await element.get_attribute("href")
        
        if href:
            email = href.replace("mailto:", "").strip()
            
            if email.endswith(domaines_autoriser):
                print("email :", email)
                await ajouter_dans_fichier("emails_collecter.json", {"email": email, "nom": nom_page}, "email", email)
    
    await mettre_a_jour("pages_collecter2.json", {"verfierEmail": 1}, "page", url)
    

        
async def message(page, nom, url):
    message_btn = await page.query_selector('div[aria-label="Message"]') # verifier si ya le btn message sur la page
    if message_btn:
        print("📩 message disponible")
        await ajouter_dans_fichier("pages_collecter_artistes.json", {"message": url, "nom": nom}, "message", url)
    else:
        print("❌ pas de message")
        


async def recuperer_lien(context, page):
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
                
                contenu = await charger_fichier("pages_collecter_artistes.json") or []
                
                url_existe_deja = False 
                for p in contenu: # verifier si url existe deja dans db
                    if p.get("url") == url: 
                        print("url existe déjà")
                        url_existe_deja = True
                        break 

                if url_existe_deja: continue  # si url_existe_deja=True, on passe à l'url suivante
                seen.add(url)
                print("Ouverture :", url)
                
                try:
                    new_page = await context.new_page()
                    await new_page.goto(url)
                    nom = await nom_page(new_page, url); #sauvegarder le lien du compte ami
                        
                    await new_page.close()
                except Exception as e:
                    print("cc.."); print(e) #en general, ici l'erreur cest quand ca a trop charger la page longtemps
                    await new_page.close()

            # Scroll pour charger plus de contenu 
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            print("patiente 1s"); await asyncio.sleep(1)
            
        except Exception as e:
            print("..erreur"); #print(e)
        
        
async def verifier_dernier_mot():
    fichier_mot_debut = "mot_cles_artistes_debut.json" # dernier_mot_cle.json
    mot_debut = (await charger_fichier_d(fichier_mot_debut)).get("mot_cle")
    
    fichier_mot = "mot_cles_artistes.json"
    mots = await charger_fichier(fichier_mot) # Charger la liste de mots cles
    
    if mot_debut:
        # Si un dernier mot est enregistré, trouver son index
        for mot in mots:
            if mot == mot_debut:
                mot_debut = mot
                break
                
    return mots, mot_debut, fichier_mot_debut


async def collecter_liens(fichier, context, page):
    await page.goto("https://fb.com", timeout=0)
    await verifier_blocage2(context, page, fichier)
    await basculer_sur_le_compte(page)
   
    #print(f"mot_debut : {mot_debut}")
    
    
    while True:
        mots, mot_debut, fichier_mot_debut = await verifier_dernier_mot()
         
        start_index = 0
        if mot_debut:
            if mot_debut in mots:
                start_index = mots.index(mot_debut) # Trouver l'index du mot de début
                
        for i in range(start_index, len(mots)):
            mot = mots[i]

            if i+1 < len(mots): mot_suivant = mots[i+1]
            else: mot_suivant = ""
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
                    
                    await clic_div_aria_label_role_button(page, ["Fermer"], cliquer=True)
                    
                except Exception as e:
                    print("..erreur"); print(e) #en general, ici l'erreur cest quand ca essai de cliquer sur: Publications récentes, et ca rate parfois, et quand ca rate il scrolle juste et prend les pages avec post recent/et non recent
        
            await recuperer_lien(context, page)
            await sauvegarder_fichier(fichier_mot_debut, { "mot_cle": mot_suivant })
    


async def numero_telephone(page):

    # numero dans la bio
    numero_bio = await page.evaluate('''() => {
        const spans = [...document.querySelectorAll('span[dir="auto"]')];
        for (const s of spans) {
            const texte = s.textContent;
            const match = texte.match(/\\+\\d{1,3}[\\s\\d]{6,}/);
            if (match) {
                return match[0].replace(/\\s+/g, '').trim();
            }
        }
        return null;
    }''')
    
    
    # numero dans le span
    numero_span = await page.evaluate("""
    () => {
        const spans = [...document.querySelectorAll('div[role="listitem"] span[dir="auto"]')];
        const trouve = spans
            .map(s => s.textContent.trim())
            .find(t => /^\\+\\d/.test(t)) || null;
        return trouve ? trouve.replace(/\\s+/g, '') : null;
    }
    """)
    
    print("numero_bio:", numero_bio)
    print("numero_span ", numero_span); return numero_bio, numero_span
    
    
    
    
async def reparer_numero(page, url):
    await page.goto(url, timeout=0)
    
    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)") # Scroll pour descendre en bas, (je descend en bas pour pouvoir afficher le numero span)
    print("patiente 5s"); await asyncio.sleep(5)
    
    numero_bio, numero_span = await numero_telephone(page);
    if numero_bio or numero_span: 
        print("numéro trouvé"); 
        
        if numero_bio == numero_span:  # ✅ si les deux sont identiques, on enregistre juste telephone_bio
            data = {"telephone_bio": numero_bio}
        else:            
            data = {}
            if numero_bio:
                data["telephone_bio"] = numero_bio
                
            if numero_span:
                data["telephone_span"] = numero_span
            
            
        await mettre_a_jour("pages_collecter_artistes2.json", data, "url", url)
        await mettre_a_jour("artistes2.json", data, "url", url)
    else:
        print("pas de numero"); 
        await mettre_a_jour("artistes2.json", {"telephone": 0}, "url", url)
                    
                    
                    
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(        
        headless=False, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars", "--disable-web-security"])
        fichier1 = "pages_collecter_artistes2.json"
        fichier2 = "artistes2.json"
        
        pages_fb = await verifier_nouveau_element(fichier1, fichier2, "url")
        pages_fb = [p for p in pages_fb if "url" in p]
        pages_fb = [p for p in pages_fb if await verifier_date_recontacte(p)]
        pages_fb = [p for p in pages_fb if not p.get("telephone") and not p.get("telephone_bio") and not p.get("telephone_span")]
        pages_fb = [p for p in pages_fb if not p.get("nom", "").strip().startswith("-")]  # exclut celles qui commencent par -
        #pages_fb = [p for p in pages_fb if p.get("nom", "").strip().startswith("+")]  # ne garde que les pages qui ont + devant leur nom
        
        fichier3 = "mes_comptes_fb.json"
        fichier4 = "mes_comptes_fb2.json"
        comptes_fb = await verifier_nouveau_element(fichier3, fichier4, "btn_message")
        comptes_fb = [c for c in comptes_fb if await verifier_date_recontacte(c) and c.get("envoyer_message") == 1]
        
        fichier_page_message_debut = "artistes_debut.json"
        page_message_debut = (await charger_fichier_d(fichier_page_message_debut)).get("url")
        
        index = next((i for i, page in enumerate(pages_fb) if page.get("url") == page_message_debut), 0)
        page_suivant = None
        pages_deja_contacter = set()
        tour = 0

        if len(comptes_fb) == 0: print("Tout les comptes ont été utilisés")

        for compte_fb in comptes_fb:  # 🔁 boucle EXTERNE : un compte à la fois
            fichier_cookie = compte_fb.get("fichier")
            mon_compte = compte_fb.get("fichier")

            while index < len(pages_fb):  # 🔁 boucle INTERNE : toutes les pages pour CE compte
                tour += 1
                print("index ", index)

                page = pages_fb[index]
                url_page = page.get("url")

                if url_page in pages_deja_contacter:
                    index += 1
                    continue

                context = await browser.new_context()
                cookies = charger_cookies(fichier_cookie)
                await context.add_cookies(cookies)

                page = await context.new_page()
                await apply_stealth(page)
                print("✅ mon_compte : ", mon_compte)
                print("Contacté :", url_page)

                try:
                    await reparer_numero(page, url_page)
                except Exception as e:
                    print("..erreur main", e)

                await verifier_commande(page, 10)
                await sauvegarder_cookies(context, fichier_cookie)
                await context.close()

                pages_deja_contacter.add(url_page)
                index += 1

                #statut = await tour_suivant(fichier_page_message_debut, pages_fb, comptes_fb, page_suivant, tour, index, "url", "compte")
                #if statut == "tout_mes_comptes_utiliser": break

            print(f"✅ Compte {mon_compte} a fini de contacter toutes les pages disponibles")

        print("Tous les comptes ont contacté toutes les pages")

asyncio.run(main())

