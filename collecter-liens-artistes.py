import json, asyncio, msvcrt, time, unicodedata, subprocess, sys
from playwright.async_api import async_playwright
from itertools import cycle
from outils_playwright import (connecter_gmail, clic_div_aria_label_role_button, sauvegarder_cookies, charger_cookies, sauvegarder_fichier, charger_fichier, 
charger_fichier_d, ajouter_dans_fichier, mettre_a_jour, post_recent, verifier_blocage2, nettoyer_texte, mots_inutiles, domaines_autoriser, clic_div_aria_label_role_button,
query_selector_text, compter_followers_fb, numero_telephone)




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
    
    


"""
Module générique de stockage SQLite, réutilisable pour n'importe quel projet
de scraping (Facebook, emails, etc.).

Principe : chaque projet définit son propre schéma (nom de fichier, nom de
table, colonnes, colonne unique pour les doublons) et utilise les mêmes
fonctions génériques pour créer, vérifier et insérer.

Exemple d'utilisation en bas du fichier.
"""

import sqlite3


def init_db(db_path, table_name, colonnes, colonne_unique):
    """
    Crée (si besoin) la base et la table.

    db_path        : chemin du fichier .db, ex "pages_artistes.db"
    table_name     : nom de la table, ex "pages"
    colonnes       : dict {nom_colonne: type_sql}, ex {"nom": "TEXT", "url": "TEXT", "telephone": "TEXT"}
    colonne_unique : nom de la colonne qui ne doit jamais avoir de doublon, ex "url"

    Retourne la connexion, à garder ouverte pendant toute la durée du script.
    """
    conn = sqlite3.connect(db_path)

    definitions = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
    for nom_col, type_col in colonnes.items():
        suffixe = " UNIQUE" if nom_col == colonne_unique else ""
        definitions.append(f"{nom_col} {type_col}{suffixe}")
    definitions.append("date_collecte DATETIME DEFAULT CURRENT_TIMESTAMP")

    requete = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(definitions)})"
    conn.execute(requete)
    conn.commit()
    return conn


def existe_deja(conn, table_name, colonne, valeur):
    """Vérifie si une valeur existe déjà dans une colonne (rapide, via l'index)."""
    requete = f"SELECT 1 FROM {table_name} WHERE {colonne} = ? LIMIT 1"
    cur = conn.execute(requete, (valeur,))
    return cur.fetchone() is not None


def sauvegarder(conn, table_name, donnees: dict):
    """
    Insère une ligne. Ignore silencieusement si la colonne UNIQUE existe déjà.

    donnees : dict {nom_colonne: valeur}, ex {"nom": "Flavio", "url": "https://..."}
    Retourne True si insérée, False si doublon ignoré.
    """
    colonnes = ", ".join(donnees.keys())
    points_interrogation = ", ".join("?" for _ in donnees)
    requete = f"INSERT OR IGNORE INTO {table_name} ({colonnes}) VALUES ({points_interrogation})"

    cur = conn.execute(requete, tuple(donnees.values()))
    conn.commit()
    return cur.rowcount > 0




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
                    

        
async def nom_page(conn1, conn2, conn3, page, url):
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
        sauvegarder(conn1, "pages", {"nom": name, "url": url, "ami": 1}) #lien du compte ami
    else:
        sauvegarder(conn1, "pages", {"nom": name, "url": url}) # on sauvegarde quand meme l'url (car quand ca sera en marche, notre robot saura qu'on a deja traité cet url)

        statut = await query_selector_text(page, ["Artiste", "Musique/groupe", "Groupe", "Rappeur"])
        if statut: 
            
            follower = await compter_followers_fb(page)
            if follower is not None and follower < 10000:
                print("artiste trouvé"); 
                sauvegarder(conn1, "pages", {"nom": name, "url": url})  # sauvegarder la page trouvée
                sauvegarder(conn2, "pages", {"nom": name, "url": url})
                await numero_telephone(conn2, conn3, page, url);
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
        


async def recuperer_lien(conn1, conn2, conn3, context, page):    
    debut = time.monotonic()
    seen = set()
    
    blacklist = [ "/posts/", "/videos/", "/groups/", "sharer", "login", "privacy", "/photo/", "/61", "/pages", "/hashtag", "afad/", "groupslanding/",
        "notifications", "ad_campaign", "/professional_dashboard", "/reel", "l.facebook.com", "/onthisday", "/saved", "/ad_center", "/permalink.php", "/latest",
        "/friends_likes", "/photos", "/about", "/mentions", "/followers", "following"
    ]

    while True:
        try:
            if time.monotonic() - debut > 60 * 5: print("⏹️ Fin des 5 minutes"); return "liberer_memoire" # stop après 3 minutes 
            #if time.monotonic() - debut > 60 * 5: print("⏹️ Fin des 5 minutes"); break # stop après 3 minutes 
            
            
            links = await page.query_selector_all('[data-ad-rendering-role="profile_name"] a[href]')
            print(f"Trouvé {len(links)} liens")

            for link in links:
                url = await link.get_attribute("href")
                
                if "profile.php" in url:
                    url = url.split("&")[0]
                else:
                    url = url.split("?")[0]
                
                if not url: continue 
                if url in seen: continue # Skip, déjà vu pendant CETTE session (RAM, rapide)
                
                if "-" in url or "%" in url: continue
                if any(x in url for x in blacklist): continue # Skip blacklist
                
                # Vérification en base (remplace la lecture du JSON)
                if existe_deja(conn1, "pages", "url", url):
                    print("url existe déjà aa")
                    seen.add(url)
                    continue # si url existe_deja, on passe à l'url suivante

                seen.add(url)
                print("Ouverture :", url)
                
                try:
                    #if time.monotonic() - debut > 60 * 5: print("⏹️ Fin des 5 minutes aa"); return "liberer_memoire" # on libere la memoire après 3 minutes  
                    
                    new_page = await context.new_page()
                    await new_page.goto(url)
                    nom = await nom_page(conn1, conn2, conn3, new_page, url); #sauvegarder le lien du compte ami
                                        
                    await new_page.close()
                except Exception as e:
                    print("cc.."); print(e) #en general, ici l'erreur cest quand ca a trop charger la page longtemps
                    #print("liberer_memoire aa"); return "liberer_memoire";
                    await new_page.close()

            
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)") # Scroll pour charger plus de contenu 
            print("patiente 1s"); await asyncio.sleep(1)
            
        except Exception as e:
            #print("..erreur"); #print(e)
            print("liberer_memoire bb"); return "liberer_memoire";
        
        
        
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




async def collecter_liens(conn1, conn2, conn3, fichier, context, page):
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
        
            statut = await recuperer_lien(conn1, conn2, conn3, context, page)
            
            
            await sauvegarder_fichier(fichier_mot_debut, { "mot_cle": mot_suivant })
            
            if statut == "liberer_memoire": print("❌ on stop, Pour libérer la mémoire"); return
    
    
    
async def main():
    
    conn1 = init_db(
        db_path="pages_collecter_artistes.db",
        table_name="pages",
        colonnes={"nom": "TEXT", "url": "TEXT", "ami": "INTEGER"},
        colonne_unique="url",
    )
    
    conn2 = init_db(
        db_path="pages_collecter_artistes2.db",
        table_name="pages",
        colonnes={"nom": "TEXT", "url": "TEXT"},
        colonne_unique="url",
    )
    
    conn3 = init_db(
        db_path="artistes2.db",
        table_name="pages",
        colonnes={"nom": "TEXT", "url": "TEXT"},
        colonne_unique="url",
    )
    
    async with async_playwright() as p:
        fichier_des_comptes = "mes_comptes_fb2.json"
        comptes = await charger_comptes(fichier_des_comptes)
        comptes = [c for c in comptes if c.get("message") == 1] # message_speciale
        comptes = [c for c in comptes if not str(c.get("fichier", "")).strip().startswith("-")] # ignorer les comptes qui commencent par -
        
        #count = 0
        while True: 
            for compte in comptes:
                try:
                    #browser = await p.chromium.launch(        
                    #headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars", "--disable-web-security"])
                    
                    browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-infobars",
                        "--disable-web-security",
                        "--disable-dev-shm-usage",     # évite d'utiliser /dev/shm (souvent limité)
                        "--disable-gpu",
                        "--js-flags=--max-old-space-size=256",  # limite la mémoire JS par processus
                        "--single-process",             # un seul processus Chromium au lieu de plusieurs (risqué mais économe)
                    ])

                    
                    #fichier_cookie = compte["fichier"]
                    fichier_cookie = compte.get("fichier")
                    nomDeMonCompte = compte.get("id_inchangeable")
                    
                    print("✅", nomDeMonCompte); #print(name); print(url_page);
                    #print("patiente 60s avant de close"); await asyncio.sleep(60)
                    context = await browser.new_context() #nouveau contexte pour chaque compte
                    
                    cookies = charger_cookies(fichier_cookie) # Charger les cookies AVANT d'ouvrir la page
                    await context.add_cookies(cookies)

                    page = await context.new_page()
                    await apply_stealth(page)
                    await collecter_liens(conn1, conn2, conn3, fichier_cookie, context, page)
                                    
                    #await sauvegarder_fichier(fichier_derniere_page, {"name": name}) # ✅ sauvegarde de la dernière page
                    #await sauvegarder_cookies(context, fichier_cookie)
                    await browser.close()
                except Exception as e:
                    print(e);
                
            #count += 1
            
    conn1.close()
    conn2.close()
    conn3.close()


if __name__ == "__main__":
    asyncio.run(main())
