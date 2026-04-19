import json, asyncio, os, time
from itertools import cycle
from playwright.async_api import async_playwright 
from outils_playwright import (basculer_sur_la_page, verifier_blocage, appliquer_stealth, charger_cookies)
from datetime import datetime, timedelta

url_fb = "https://fb.com"



async def verifier_compte_disponible(heure_dernier_like, nom_compte):
    dernier_passage = heure_dernier_like.get(nom_compte)

    if not dernier_passage:
        return True

    date_dernier_passage = datetime.fromisoformat(dernier_passage)
    return datetime.now() - date_dernier_passage >= timedelta(hours=1)



async def get_prochain_démarrage(dernier_passage_iso):
    dernier_passage = datetime.fromisoformat(dernier_passage_iso)
    prochain = dernier_passage + timedelta(hours=1)
    return prochain.strftime("%Y-%m-%d %H:%M:%S")
    
    
    

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



# Posts liker
def post_deja_liker(posts, lien):
    if not lien:
        return False

    return lien in posts
    
           
def ajouter_post(posts, fichier, lien):
    if lien not in posts:
        posts.append(lien)
        sauvegarder_json(fichier, posts)



async def recuperer_texte(page, context, posts, url_page, fichier_posts):
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:        
        element = page.locator('[data-ad-rendering-role="story_message"]').first
        texte = await element.text_content()
        
        # ICI on coupe à 500 caractères pour eviter les tres long texte dans mon fichier
        identifiant_post = " ".join(texte.split())[:500] #print(f"Texte : {identifiant_post[:80]}")
        
        if posts and post_deja_liker(posts, identifiant_post): 
            return "deja_liker" #print(f"Déjà liké") # Vérification déjà liké

        # Sauvegarde texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post) #print("Texte sauvegardé")
    except:
        pass
        #print("Impossible de récupérer le texte :", e)
        
    # RÉCUPÉRATION LIEN
    source_post = page.locator('[role="article"]').nth(0)
    link_locator = source_post.locator("a[href*='/posts/'], a[href*='/videos/']")
    count_link = await link_locator.count()

    if count_link > 0:
        post_link = await link_locator.first.get_attribute("href") #print("lien trouvé :", post_link)
    else:
        post_link = None
    
      
      
async def post_recent(page, context, url_page):
    print("patiente 4s"); await asyncio.sleep(4)
    await page.goto(url_page, timeout=0) 
    print("patiente 2s"); await asyncio.sleep(2)
    
    element = await page.query_selector("text=Ce contenu n’est pas disponible pour le moment")
    if element: return "compte_inexistant" #print("Compte inexistant"); 
    
    
    fichier_posts = "posts_deja_commentes.json"
    posts = charger_posts(fichier_posts)
        
    statut = await recuperer_texte(page, context, posts, url_page, fichier_posts) # Vérifier si posts deja commentes
    if statut == "deja_liker": return "deja_liker" #print("Déjà liké"); 
        
        
    btn = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    if await btn.count() > 0:    
        await btn.click()
        print("patiente 2s"); await asyncio.sleep(2); 
        



async def liker_post(page, context, url_page):    
    await page.goto(url_fb, timeout=0) 
    
    statut = await verifier_blocage(page)
    if statut == "bloquer_selfie_video": print("⛔ bloqué selfie video"); return
    
    
    btn = await page.query_selector("text=Tableau de bord")
    if btn:
        print("Connecté sur la page")
        
        statut = await post_recent(page, context, url_page)
        if statut == "compte_inexistant": print("❌ Compte inexistant"); return
        if statut == "deja_liker": print("❌ Déjà liké"); return
    else:
        await basculer_sur_la_page(page)
        
        statut = await post_recent(page, context, url_page)
        if statut == "compte_inexistant": print("❌ Compte inexistant"); return
        if statut == "deja_liker": print("❌ Déjà liké"); return
        
        
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
            headless=False,
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
        
        patience_affichee = {}
        while True:
            for page_info in pages_list:
                compte = next(cycle_comptes); 
                if compte["fichier"].startswith("-"): continue #ignorer les comptes qui commencent par "-"
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("id_inchangeable")
                
                
                if not await verifier_compte_disponible(heure_dernier_like, nomDeMonCompte):
                    if not patience_affichee.get(nomDeMonCompte, False):
                        dernier_passage = heure_dernier_like.get(nomDeMonCompte)
                        if dernier_passage:
                            date_next = await get_prochain_démarrage(dernier_passage)
                            print(f"{nomDeMonCompte} : Prochain démarrage prévu le {date_next}")
                        else:
                            print(f"{nomDeMonCompte} : Patiente 1h")  # fallback
                        patience_affichee[nomDeMonCompte] = True
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
                cookies = charger_cookies(fichier_cookie)
                await context.add_cookies(cookies)
                
                page = await context.new_page()
                await appliquer_stealth(page)
                
                await liker_post(page, context, url_page)
                heure_dernier_like[nomDeMonCompte] = datetime.now().isoformat()
                await sauvegarder_fichier(fichier_heure_dernier_like, heure_dernier_like)

                await sauvegarder_derniere_page(name) # ✅ sauvegarde de la dernière page
                await context.close() #fermer le contexte (ou la fenetre)
            #await context.close()   
            
        #await asyncio.sleep(10000) 
        #await context.close()

if __name__ == "__main__":
    asyncio.run(main())
