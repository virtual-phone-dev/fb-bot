import json, asyncio, os, time, math
from itertools import cycle
from playwright.async_api import async_playwright 
from outils_playwright import (basculer_sur_la_page, verifier_blocage, appliquer_stealth, charger_cookies, charger_fichier)
from datetime import datetime, timedelta

url_fb = "https://fb.com"



async def sauvegarder_fichier(fichier, data):
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        


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
    
    await basculer_sur_la_page(page)

    statut = await post_recent(page, context, url_page)
    if statut == "compte_inexistant": print("❌ Compte inexistant"); return
    if statut == "deja_liker": 
        print("❌ Déjà liké"); 
        
        page_30jours = await charger_json("page_30jours.json") # page_30jours (déja liker, on sauvegarde la page dans page_30jours
        page_30jours.append(url_page)
        await sauvegarder_fichier("page_30jours.json", page_30jours)
        return
    
    page_active = await charger_json("page_active.json") # page_active (pas encore liker, on sauvegarde la page dans page_active
    page_active.append(url_page)
    await sauvegarder_fichier("page_active.json", page_active)

        
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
        
        pages_list = await charger_fichier("pages-tout-pays.json") # Charger la liste de pages
        comptes = await charger_fichier("comptes-fb.json")   
        derniere_page = charger_derniere_page() 
        debut = False

        #FILTRAGE AVANT
        comptes = [c for c in comptes if not c["fichier"].startswith("-")]
        pages_list = [p for p in pages_list if "url" in p]
        cycle_pages = cycle(pages_list)
        
        while True:                       
            for compte in comptes:
                page = next(cycle_pages); 
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("id_inchangeable")

                url_page = page.get('url')
                name = page.get('name');
                
                #if not url_page: continue  #ignorer les zones
                
                if derniere_page:
                    if derniere_page == name: debut = True
                    if not debut: continue
                
                print("✅", nomDeMonCompte); print(name); print(url_page);
                    
                # Charger les cookies AVANT d'ouvrir la page
                context = await browser.new_context() #nouveau contexte pour chaque compte
                cookies = charger_cookies(fichier_cookie)
                await context.add_cookies(cookies)
                
                page = await context.new_page()
                await appliquer_stealth(page)
                await liker_post(page, context, url_page)
                
                await sauvegarder_derniere_page(name) # ✅ sauvegarde de la dernière page
                await context.close() #fermer le contexte (ou la fenetre)

            if debut: 
                print("✅ Patiente 30 minutes"); await asyncio.sleep(60 * 30)
            

if __name__ == "__main__":
    asyncio.run(main())
