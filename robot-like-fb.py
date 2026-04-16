import json, asyncio, os, time
from itertools import cycle
from playwright.async_api import async_playwright 
from outils_playwright import (basculer_sur_la_page)

url_fb = "https://fb.com"


async def charger_comptes(fichier_des_comptes):
    with open(fichier_des_comptes, "r", encoding="utf-8") as f:
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


def sauvegarder_derniere_page(name):
    with open("derniere_page.json", "w", encoding="utf-8") as f:
        json.dump({"name": name}, f, indent=4, ensure_ascii=False)
  


async def apply_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] }); """)


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

        
        
        
async def post_recent(page, url_page):
    print("patiente 4s"); await asyncio.sleep(4)
    await page.goto(url_page, timeout=0) 
    print("patiente 2s"); await asyncio.sleep(2)
                
    btn = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    if await btn.count() > 0:    
        await btn.click()
        print("patiente 2s"); await asyncio.sleep(2); 



async def liker_post(page, context, url_page):
    await page.goto(url_fb, timeout=0) 
    
    print("patiente 2s"); await asyncio.sleep(2)
    btn = await page.query_selector("text=Tableau de bord professionnel")
    if btn:
        print("Connecté sur la page")
        await post_recent(page, url_page)
    else:
        await basculer_sur_la_page(page)
        await post_recent(page, url_page)
        
        
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
                    
            # Récupérer le nombre total de clics
            #total_clics = await page.evaluate("window.clickCount")
            #print(f"Nombre total de clics effectués : {total_clics}"); print("Terminé.")
            #break
    #await context.close()
    
    
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

        derniere_page = charger_derniere_page()
        demarrer = False if derniere_page else True # si aucune sauvegarde → on commence directement
        
        # Charger la liste de pages
        with open('pages-tout-pays.json', 'r', encoding='utf-8') as f:
            pages_list = json.load(f)
        
        # ✅ FILTRAGE AVANT
        comptes = [c for c in comptes if not c["fichier"].startswith("-")]
        pages_list = [p for p in pages_list if "url" in p]
        cycle_comptes = cycle(comptes)
        
        for page_info in pages_list:
            
            compte = next(cycle_comptes)
            if compte["fichier"].startswith("-"): continue #ignorer les comptes qui commencent par "-"
            fichier_cookie = compte.get("fichier")
            
            url_page = page_info.get('url')
            name = page_info.get('name', 'Inconnu')
            
            #if not url_page: continue  #ignorer les zones
            
            # reprise à partir de la dernière page
            if not demarrer:
                if name == derniere_page:
                    demarrer = True
                else:
                    continue
            
            #print(f"Traitement de {name} : {url_page}")
            print(name); print(url_page);
                
            # Charger les cookies AVANT d'ouvrir la page
            context = await browser.new_context() #nouveau contexte pour chaque compte
            cookies = load_cookies(fichier_cookie)
            await context.add_cookies(cookies)
                
            page = await context.new_page()
            await apply_stealth(page)
            
            await liker_post(page, context, url_page)
            sauvegarder_derniere_page(name) # ✅ sauvegarde de la dernière page
            await context.close() #fermer le contexte (ou la fenetre)
                
        await asyncio.sleep(10000)


if __name__ == "__main__":
    asyncio.run(main())
