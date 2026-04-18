import json, asyncio, os, time
from itertools import cycle
from playwright.async_api import async_playwright 
from outils_playwright import (basculer_sur_la_page, appliquer_stealth)

url_fb = "https://fb.com"



async def charger_comptes(fichier_des_comptes):
    with open(fichier_des_comptes, "r", encoding="utf-8") as f:
        return json.load(f)
        
      
def charger_posts(fichier):
    if not os.path.exists(fichier):
        return []
    with open(fichier, "r", encoding="utf-8") as f:
        return json.load(f)

        
async def save_cookies(context):
    print("patiente 7s")
    await asyncio.sleep(7)
    
    print("on sauvegarde les cookies")
    cookies = await context.cookies()
    with open(fichier_cookie, "w") as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)

    print("cookies sauvegardé")
    


def charger_derniere_page():
    if not os.path.exists("derniere_page.json"):
        return None
    try:
        with open("derniere_page.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("name")
    except:
        return None
        

async def sauvegarder_derniere_page(name):
    with open("derniere_page.json", "w", encoding="utf-8") as f:
        json.dump({"name": name}, f, indent=4, ensure_ascii=False)
  
  
def sauvegarder_json(fichier, data):
    with open(fichier,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)



async def charger_fichier(fichier):
    if not os.path.exists(fichier):
        return {}
    with open(fichier, "r", encoding="utf-8") as f:
        return json.load(f)


async def sauvegarder_fichier(fichier, data):
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


async def verifier_compte_disponible(heure_dernier_like, nom_compte):
    dernier_passage = heure_dernier_like.get(nom_compte)

    if not dernier_passage:
        return True

    date_dernier = datetime.fromisoformat(dernier_passage)
    return datetime.now() - date_dernier >= timedelta(hours=1)
    
    

# Posts commentés
def post_deja_commente(posts, lien):
    if not lien:
        return False

    return lien in posts
    
           
def ajouter_post(posts, fichier, lien):
    if lien not in posts:
        posts.append(lien)
        sauvegarder_json(fichier, posts)
        
        

def load_cookies(fichier_cookie):
    if not os.path.exists(fichier_cookie):
        return []

    try:
        with open(fichier_cookie, "r", encoding="utf-8") as f:
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



async def recuperer_texte(page, context, posts, url_page, fichier_posts):
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:        
        element = page.locator('[data-ad-rendering-role="story_message"]').first
        texte = await element.text_content()
        
        # ICI on coupe à 500 caractères
        identifiant_post = " ".join(texte.split())[:500]
        #print(f"Texte : {identifiant_post[:80]}")

        # Vérification déjà commenté
        if posts and post_deja_commente(posts, identifiant_post):
            #print(f"Déjà commenté")

            #if context:
            #    await page.close()
            #    await context.close()

            return True

        # Sauvegarde texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post)
            #print("Texte sauvegardé")

    except:
        pass
        #print("Impossible de récupérer le texte :", e)
        #return False
        
        
    # RÉCUPÉRATION LIEN
    source_post = page.locator('[role="article"]').nth(0)
    link_locator = source_post.locator("a[href*='/posts/'], a[href*='/videos/']")
    count_link = await link_locator.count()

    if count_link > 0:
        post_link = await link_locator.first.get_attribute("href")
        #print("lien trouvé :", post_link)
    else:
        post_link = None
    
      
      
async def post_recent(page, context, url_page):
    print("patiente 4s"); await asyncio.sleep(4)
    await page.goto(url_page, timeout=0) 
    print("patiente 2s"); await asyncio.sleep(2)
    
    element = await page.query_selector("text=Ce contenu n’est pas disponible pour le moment")
    if element:
        print("❌ Compte inexistant"); return
            
        
    fichier_posts = "posts_deja_commentes.json"
    posts = charger_posts(fichier_posts)    
        
    stop = await recuperer_texte(page, context, posts, url_page, fichier_posts) # Vérifier si posts deja commentes
    if stop:
        print("❌ Déjà liké")
        return
                    
    btn = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    if await btn.count() > 0:    
        await btn.click()
        print("patiente 2s"); await asyncio.sleep(2); 
            


async def liker_post(page, context, url_page):    
    await page.goto(url_fb, timeout=0) 
        
    print("patiente 5s"); await asyncio.sleep(5)
    btn = await page.query_selector("text=Tableau de bord")
    if btn:
        print("Connecté sur la page")
        await post_recent(page, context, url_page)
    else:
        await basculer_sur_la_page(page)
        await post_recent(page, context, url_page)
            
            
    temps_debut = time.monotonic()  # Enregistre le temps de début
    temps = 10
            
    while True:
        # Vérifie si le temps écoulé dépasse 30 secondes
        temps_ecouler = time.monotonic() - temps_debut
        if temps_ecouler > temps:
            print("Temps écoulé, arrêt")
            break
                
        btn = page.get_by_label("J’aime")
        if await btn.count() > 0:                                               
            await page.evaluate("""
            const buttons = document.querySelectorAll('div[aria-label="J’aime"]');
            for (let i = 0; i < Math.min(20, buttons.length); i++) {
              buttons[i].scrollIntoView({ behavior: "smooth", block: "center" });
              buttons[i].click();
            } """)
            
    
    
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
        
        comptes = await charger_comptes("comptes-fb.json")   
        
        fichier_heure_dernier_like = "heure_dernier_like.json"
        heure_dernier_like = await charger_fichier(fichier_heure_dernier_like)
        
        derniere_page = charger_derniere_page() 
        demarrer = False if derniere_page else True
        
        # Charger la liste de pages
        with open('pages-tout-pays.json', 'r', encoding='utf-8') as f:
            pages_list = json.load(f)
            
            
        #FILTRAGE AVANT
        comptes = [c for c in comptes if not c["fichier"].startswith("-")]
        pages_list = [p for p in pages_list if "url" in p]
        cycle_comptes = cycle(comptes)
        
        while True:
            for page_info in pages_list:
                compte = next(cycle_comptes); 
                if compte["fichier"].startswith("-"): continue #ignorer les comptes qui commencent par "-"
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("id_inchangeable")
                
                if not verifier_compte_disponible(heure_dernier_like, nomDeMonCompte):
                    print(f"{nomDeMonCompte} : Patiente 1h)")
                    continue
                
                url_page = page_info.get('url')
                name = page_info.get('name', 'Inconnu')
                
                #if not url_page: continue  #ignorer les zones
                
                if not demarrer:
                    if name == derniere_page:
                        demarrer = True
                    else:
                        continue
                            
                #print(f"Traitement de {name} : {url_page}")
                print("✅", nomDeMonCompte); print(name); print(url_page);
                    
                # Charger les cookies AVANT d'ouvrir la page
                context = await browser.new_context() #nouveau contexte pour chaque compte
                cookies = load_cookies(fichier_cookie)
                await context.add_cookies(cookies)
                
                page = await context.new_page()
                await appliquer_stealth(page)
                
                await liker_post(page, context, url_page)
                heure_dernier_like[nomDeMonCompte] = datetime.now().isoformat()
                await sauvegarder_fichier(fichier_heure_dernier_like, heure_dernier_like)

                await sauvegarder_derniere_page(name) # ✅ sauvegarde de la dernière page
                await context.close() #fermer le contexte (ou la fenetre)
                
        #await asyncio.sleep(10000)


if __name__ == "__main__":
    asyncio.run(main())
