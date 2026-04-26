import asyncio
from itertools import cycle;
from playwright.async_api import async_playwright
from outils_playwright import (creer_context, creer_page, aller, appliquer_stealth, charger_cookies, charger_fichier, sauvegarder_fichier, sauvegarder_cookies)

FICHIER_POSTS = "sauvegarde-bs/posts_commentes.json"
FICHIER_BLACKLIST = "sauvegarde-bs/blacklist.json"
url_post = "https://bsky.app/profile/bbcnewsnight.bsky.social/"

# <button aria-label="Aimer (0 ont aimé)" aria-pressed="false" role="button" tabindex="0" class="css-g5y9jx r-1loqt21 r-1otgn73" data-testid="likeBtn" type="button" style="justify-content: center; border-radius: 999px; flex-direction: row; align-items: center; gap: 4px; background-color: rgba(0, 0, 0, 0); padding: 5px;"><div class="css-g5y9jx"><svg fill="none" width="18" viewBox="0 0 24 24" height="18" style="color: rgb(102, 123, 153); pointer-events: none;"><path fill="#667B99" stroke="none" stroke-width="0" stroke-linecap="butt" stroke-linejoin="miter" fill-rule="evenodd" clip-rule="evenodd" d="M16.734 5.091c-1.238-.276-2.708.047-4.022 1.38a1 1 0 0 1-1.424 0C9.974 5.137 8.504 4.814 7.266 5.09c-1.263.282-2.379 1.206-2.92 2.556C3.33 10.18 4.252 14.84 12 19.348c7.747-4.508 8.67-9.168 7.654-11.7-.541-1.351-1.657-2.275-2.92-2.557Zm4.777 1.812c1.604 4-.494 9.69-9.022 14.47a1 1 0 0 1-.978 0C2.983 16.592.885 10.902 2.49 6.902c.779-1.942 2.414-3.334 4.342-3.764 1.697-.378 3.552.003 5.169 1.286 1.617-1.283 3.472-1.664 5.17-1.286 1.927.43 3.562 1.822 4.34 3.764Z"></path></svg><div class="css-g5y9jx" style="position: absolute; background-color: rgb(236, 72, 153); top: 0px; left: 0px; width: 18px; height: 18px; z-index: -1; pointer-events: none; border-radius: 9px; opacity: 0;"></div><div class="css-g5y9jx" style="position: absolute; background-color: rgb(255, 255, 255); top: 0px; left: 0px; width: 18px; height: 18px; z-index: -1; pointer-events: none; border-radius: 9px; opacity: 0;"></div></div></button>



async def visiter(browser, compte, url, comments, posts, blacklist, page_name=None):
    fichier = compte["fichier"]
    if est_blacklist(blacklist, fichier, url): print("Blacklist :", fichier, url); return

    contexte = await creer_context(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        await envoyer_commentaire_bs(page, comments, posts, FICHIER_POSTS, page_name, url, fichier)
        
    except Exception as e:
        print("Erreur :", e)
        ajouter_blacklist(blacklist, FICHIER_BLACKLIST, fichier, url)
        
    await contexte.close()



async def verifier_blocage_bs(page):
    btn = await page.query_selector("text=Votre compte a été suspendu")
    if btn:
        return "compte_desactiver"
        
        
async def connexion_bs(page, email, mot_de_passe):
    await page.goto("https://bsky.app/", timeout=0)
    await page.wait_for_load_state("domcontentloaded")

    while True:
        btn = page.locator('span:has-text("Connexion")')
        if await btn.count() > 0:
            await btn.click() #print("Non Connecté");
            
            await page.get_by_label("Pseudo ou e-mail").fill(email)
            await page.fill('input[data-testid="loginPasswordInput"]', mot_de_passe);
            #await page.fill('input[aria-label="Mot de passe"]', 'votre_mot_de_passe');
            
            print("patiente 1s"); await asyncio.sleep(1)
            await page.click('button[data-testid="loginNextButton"]');

            print("patiente 10s"); await asyncio.sleep(10)
            statut = await verifier_blocage_bs(page)
            if statut == "compte_desactiver": print("⛔ Compte désactiver"); return
            
            break
            
            
        element = await page.query_selector('a[aria-label="Paramètres"]')
        if element:
            break #print("Connecté");
    
    #print("patiente 10000s"); await asyncio.sleep(10000)
    
    
    
async def liker(page, url_page):
    await page.goto(url_page, timeout=0)
    print("patiente 5s"); await asyncio.sleep(5)
    
    fichier_posts = "posts_deja_liker_bs.json"
    posts = await charger_fichier(fichier_posts)
    
    statut = await recuperer_texte_bs(page, posts, fichier_posts) # Vérifier si posts deja liker
    if statut == "deja_liker": return #print("Déjà liké"); 
    print("patiente 10000s"); await asyncio.sleep(10000)
    
    
    element = await page.query_selector('div[data-testid="contentHider-post"]') # 🔹 trouver le premier post
    if element:
        await page.evaluate(""" const posts = document.querySelectorAll('div[data-testid="contentHider-post"]');
        if (posts.length > 0) { posts[0].click(); } """)
    
    
    print("patiente 3s"); await asyncio.sleep(3)  
    
    await page.eval_on_selector_all('button[data-testid="likeBtn"]', 'buttons => buttons.forEach(b => b.click())') # Cibler tous les boutons "J'aime" et cliquer dessus
    print("patiente 4s"); await asyncio.sleep(4)    
    
    

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])    
        comptes = await charger_fichier("comptes-bs.json")
        comptes = [c for c in comptes if not c["fichier"].startswith("-")]      

        pages_list = await charger_fichier("page_active_bs.json") # Charger la liste de pages
        pages_list = [p for p in pages_list if "url" in p]
        cycle_pages = cycle(pages_list)
        
        fichier_derniere_page = "derniere_page_bs.json"
        data = await charger_fichier_d(fichier_derniere_page)
        derniere_page = data.get("name")

        debut = False
        
        count = 0
        while count < 3: 
            for compte in comptes:
                fichier_cookie = compte["fichier"]
                
                page = next(cycle_pages); 
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("nom")

                url_page = page.get('url')
                name = page.get('name'); #print("name : ", name); print(url_page);
                                
                                
                if derniere_page:
                    if derniere_page == name: debut = True
                    if not debut: continue
                
                print("✅", nomDeMonCompte); print(name); print(url_page);
                
                context = await browser.new_context() #nouveau contexte pour chaque compte
                
                cookies = charger_cookies(fichier_cookie) # Charger les cookies AVANT d'ouvrir la page
                await context.add_cookies(cookies)
                
                #nom_complet = compte["nom_complet"]
                #nom_profil = compte["nom_profil"]
                email = compte["email"]
                mot_de_passe = compte["mot_de_passe"]
                
                print(fichier_cookie);

                page = await context.new_page()
                await appliquer_stealth(page)
                
                await connexion_bs(page, email, mot_de_passe)
                await liker(page, url_page)
                
                await sauvegarder_fichier(fichier_derniere_page, {"name": name}) # ✅ sauvegarde de la dernière page
                await sauvegarder_cookies(context, fichier_cookie)
                await context.close()
            count += 1
            
            
asyncio.run(main())

