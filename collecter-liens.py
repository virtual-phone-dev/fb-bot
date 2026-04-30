import json, asyncio
from playwright.async_api import async_playwright
from itertools import cycle
from outils_playwright import (connecter_gmail, sauvegarder_cookies, charger_cookies, sauvegarder_fichier, charger_fichier, charger_fichier_d, ajouter_dans_fichier)

#url_post = "https://www.threads.com/@laurene_mba"




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


    
 
async def verifier_btn_amis(page):
    btn = await page.query_selector('a[href*="/friends"]')
    if btn:
        print("👥 bouton amis trouvé")
    
    
async def nom_page(page):
    name = await page.locator("h1").first.text_content() # recuperer nom_page
    name = name.strip() if name else None
    print("nom_page : ", name); return name
            
            
async def email(page, nom_page):           
    element = await page.query_selector('[href^="mailto:"]') # recuperer email
    
    email = None
    if element:
        href = await element.get_attribute("href")
        if href:
            email = href.replace("mailto:", "").strip()
            await ajouter_dans_fichier("emails_collecter.json", { "email": email, "nom": nom_page })

    print("email :", email)
    
    
async def message(page):
    message_btn = await page.query_selector('div[aria-label="Message"]') # verifier si ya le btn message sur la page
    if message_btn:
        print("📩 message disponible")
    else:
        print("❌ pas de message")
        
        
    
async def recuperer_lien(page, context):
    seen = set()
    
    blacklist = [
        "/posts/", "/videos/", "/groups/", "sharer", "login", "privacy",
        "/photo/", "/61", "/pages", "/hashtag", "afad/", "groupslanding/",
        "notifications", "ad_campaign", "/professional_dashboard", "/reel",
        "/onthisday", "/saved", "/ad_center", "/permalink.php", "/latest",
        "/friends_likes", "/photos", "/about", "/mentions", "/followers", "following"
    ]

    while True:
        links = await page.query_selector_all('[data-ad-rendering-role="profile_name"] a[href]')
        print(f"Trouvé {len(links)} liens")

        for link in links:
            href = await link.get_attribute("href")
            
            if "profile.php" in href:
                href = href.split("&")[0]
            else:
                href = href.split("?")[0]
            
            
            if not href: continue 
            if href in seen: continue # Skip déjà vus            
            
            if "-" in href or "%" in href: continue
            if any(x in href for x in blacklist): continue # Skip blacklist
            

            seen.add(href)
            print("Ouverture :", href)
            
            try:
                new_page = await context.new_page()
                await new_page.goto(href)
                print("patiente 2s"); await asyncio.sleep(2)
                
                nom = await nom_page(new_page)
                await email(new_page, nom)
                await message(new_page)
                await verifier_btn_amis(new_page)
                
                print("patiente 1s"); await asyncio.sleep(1)
                await new_page.close()
            except:
                print("cc..");
                await new_page.close()

        # Scroll pour charger plus de contenu
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        print("patiente 1s"); await asyncio.sleep(1)
        
    
    
async def collecter_liens(page, context):
    await page.goto("https://fb.com", timeout=0)
    #await page.wait_for_load_state("domcontentloaded")
    
    while True:
        print("patiente 1s"); await asyncio.sleep(1)
        input_box = page.get_by_placeholder("Rechercher sur Facebook")
        if await input_box.count() > 0:            
            await input_box.fill("Fally ipupa")
            await input_box.press("Enter")
            break
                
    while True:
        print("patiente 2s"); await asyncio.sleep(2)
        btn = page.get_by_label("Publications récentes")
        if await btn.count() > 0:                                               
            await btn.click()
            break
    
    await recuperer_lien(page, context)
    
    
    
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

        fichier_des_comptes = "comptes-fb.json"
        comptes = await charger_comptes(fichier_des_comptes)
        
        #pages_list = await charger_fichier("page_active_fb.json") # Charger la liste de pages
        #pages_list = [p for p in pages_list if "url" in p]
        #cycle_pages = cycle(pages_list)
        
        #fichier_derniere_page = "derniere_page_fb.json"
        #data = await charger_fichier_d(fichier_derniere_page)
        #derniere_page = data.get("name")

        #debut = False
        
        count = 0
        while count < 2: 
            for compte in comptes:
                fichier_cookie = compte["fichier"]
                
                if compte["fichier"].startswith("-"): #ignorer les comptes qui commencent par "-"
                    continue
                    
                #if compte.get("creer") == "Oui":
                #    continue  # skip si compte déjà créé
                
                #page = next(cycle_pages); 
                fichier_cookie = compte.get("fichier")
                nomDeMonCompte = compte.get("id_inchangeable")

                #url_page = page.get('url')
                #name = page.get('name'); #print("name : ", name); print(url_page);
                                
                                
                #if derniere_page:
                #    if derniere_page == name: debut = True
                #    if not debut: continue
                
                print("✅", nomDeMonCompte); #print(name); print(url_page);
                
                context = await browser.new_context() #nouveau contexte pour chaque compte
                
                cookies = charger_cookies(fichier_cookie) # Charger les cookies AVANT d'ouvrir la page
                await context.add_cookies(cookies)
            
                #nom_complet = compte["nom_complet"]
                #nom_profil = compte["nom_profil"]
                #email = compte["email"]
                #mot_de_passe = compte["mot_de_passe"]
                
                #print(nom_complet);

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
