import json, asyncio
from playwright.async_api import async_playwright
from outils_playwright import (connecter_gmail, sauvegarder_cookies, charger_cookies, recuperer_texte_th)

url_post = "https://www.threads.com/@laurene_mba"




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
          
    await connecter_gmail(context, email)
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
                await page.goto(url_post, timeout=0)
                break
        except:
            pass  

    element = await page.query_selector("text=Continuer avec Instagram")
    if element:
        print("Continuer avec insta");
        #await creer_compte_threads(page)


            
async def liker(page, url_page):
    await page.goto(url_page, timeout=0)
    await page.wait_for_load_state("domcontentloaded")
    
    fichier_posts = "posts_deja_liker_th.json"
    posts = charger_fichier(fichier_posts)
    
    statut = await recuperer_texte_th(page, posts, fichier_posts) # Vérifier si posts deja liker
    if statut == "deja_liker": return #print("Déjà liké"); 
    print("patiente 10000s"); await asyncio.sleep(10000)
    
    
    while True:
        element = await page.query_selector('[data-pressable-container="true"]') # cliquer sur le premier élément avec cet attribut
        if element:            
            await page.evaluate(""" const element = document.querySelector('[data-pressable-container="true"]');
            if (element) { element.click(); } """)
            break
    
    print("patiente 10s"); await asyncio.sleep(10)
    
    await page.evaluate(""" const likeIcons = document.querySelectorAll('svg[aria-label="J’aime"]');
    likeIcons.forEach(icon => {
      const event = new MouseEvent('click', { view: window, bubbles: true, cancelable: true }); // Crée un événement clic
      icon.dispatchEvent(event); // Déclenche l'événement sur l'icône
    }); """)
    
    print("patiente 10000s"); await asyncio.sleep(10000)
    
    
    
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

        fichier_des_comptes = "comptes-th.json"
        comptes = await charger_comptes(fichier_des_comptes)
        
        pages_list = await charger_fichier("page_active_th.json") # Charger la liste de pages
        pages_list = [p for p in pages_list if "url" in p]
        cycle_pages = cycle(pages_list)
        
        data = await charger_fichier("derniere_page_th.json")
        derniere_page = data.get("name")
        debut = False
        
        while True: 
            for compte in comptes:
                fichier_cookie = compte["fichier"]
                
                if compte["fichier"].startswith("-"): #ignorer les comptes qui commencent par "-"
                    continue
                    
                #if compte.get("creer") == "Oui":
                #    continue  # skip si compte déjà créé
                
                page = next(cycle_pages); 
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("nom_complet")

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
                
                #print(nom_complet);

                page = await context.new_page()
                await apply_stealth(page)
                #await creer_compte_insta(page, context, compte, fichier_des_comptes, nom_complet, nom_profil, email, mot_de_passe)
                #await connecter_compte_insta(page, context, compte, fichier_des_comptes, email, mot_de_passe, nom_profil)
                
                #await commenter_th(page, email, mot_de_passe)
                #break
                
                #await reparer_th(page, context, nom_complet, email, mot_de_passe)
                await connexion_th(page, email, mot_de_passe)
                await liker(page, url_page)
                
                await sauvegarder_fichier("derniere_page_th.json", {"name": name}) # ✅ sauvegarde de la dernière page
                await sauvegarder_cookies(context, fichier_cookie)
                await context.close()
            print("patiente 10000s"); await asyncio.sleep(10000)


if __name__ == "__main__":
    asyncio.run(main())
