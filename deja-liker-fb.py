import json, asyncio, os, time, math
from playwright.async_api import async_playwright 
from datetime import datetime, timedelta
from outils_playwright import (basculer_sur_la_page, verifier_blocage, appliquer_stealth, verifier_commande,
charger_cookies, charger_fichier, sauvegarder_fichier, sauvegarder_sur_meme_ligne)

url_fb = "https://fb.com"



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
        #if posts is not None and fichier_posts:
        #    ajouter_post(posts, fichier_posts, identifiant_post) #print("Texte sauvegardé")
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
        


async def liker_post(page, context, name, url_page):    
    
    statut = await verifier_blocage(page)
    if statut == "bloquer_selfie_video": print("⛔ bloqué selfie video"); return
    
    await basculer_sur_la_page(page)

    statut = await post_recent(page, context, url_page)
    if statut == "compte_inexistant": print("❌ Compte inexistant"); return
    if statut == "deja_liker": 
        print("❌ Déjà liké"); 
        
        page_30jours = await charger_fichier("page_30jours.json") # page_30jours (déja liker, on sauvegarde la page dans page_30jours
        page_30jours.append({ "name": name, "url": url_page })
        await sauvegarder_sur_meme_ligne("page_30jours.json", page_30jours)
        return
    
    print("+ Pas encore liké"); 
    #page_active = await charger_fichier("page_active.json") # page_active (pas encore liker, on sauvegarde la page dans page_active
    #page_active.append({ "name": name, "url": url_page })
    #await sauvegarder_sur_meme_ligne("page_active.json", page_active)
    await compter_commentaire(page, name, url_page)


async def compter_commentaire(page, name, url_page):   
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

            if count > 5:
                print("arrêt → Plus de 5 commentaires")
                
                #print("+ Pas encore liké"); 
                page_active = await charger_fichier("page_active.json") #on sauvegarde les pages (Pas encore liker), qui ont plus de 5 commentaires 
                page_active.append({ "name": name, "url": url_page })
                await sauvegarder_sur_meme_ligne("page_active.json", page_active)
                break
            
    
     
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
        
        pages_list = await charger_fichier("pages-tout-pays.json") # Charger la liste de pages
        comptes = await charger_fichier("comptes-fb.json")   
        derniere_page = (await charger_fichier("derniere_page_pdj.json")).get("name") # derniere_page_pdj = derniere_page_pour_deja_liker
        debut = False

        #FILTRAGE AVANT
        comptes = [c for c in comptes if not c["fichier"].startswith("-")]
        pages_list = [p for p in pages_list if "url" in p]
        
        while True:                  
            for compte in comptes:
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("id_inchangeable")
                    
                # Charger les cookies AVANT d'ouvrir la page
                context = await browser.new_context() #nouveau contexte pour chaque compte
                cookies = charger_cookies(fichier_cookie)
                await context.add_cookies(cookies)
                    
                page = await context.new_page()
                await appliquer_stealth(page)
                await page.goto(url_fb, timeout=0) 
                
                for une_page in pages_list:
                    url_page = une_page.get('url')
                    name = une_page.get('name');
                    
                    if derniere_page:
                        if derniere_page == name: debut = True
                        if not debut: continue
                    
                    print("✅", nomDeMonCompte); print(name); print(url_page);
                        
                    await liker_post(page, context, name, url_page)
                    await sauvegarder_fichier("derniere_page_pdj.json", {"name": name}) # sauvegarde de la dernière page
                    #await verifier_commande(page, duree_pause=10); #print("patiente 10000s"); await asyncio.sleep(10000)
                    
                await context.close() #fermer le contexte (ou la fenetre)

                #if debut: 
                #    print("✅ Patiente 30 minutes"); await asyncio.sleep(60 * 30)
            

if __name__ == "__main__":
    asyncio.run(main())
