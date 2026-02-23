import json, os, asyncio


# STEALTH
async def appliquer_stealth(page):
    await page.add_init_script(
        """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
"""
    )


# COOKIES
def charger_cookies(fichier):
    # créer dossier si nécessaire
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        os.makedirs(dossier)

    # créer fichier vide si inexistant
    if not os.path.exists(fichier):
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

    # lire cookies existants
    with open(fichier, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)
        
    cookies = []
    for c in raw_cookies:
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
    
    

async def sauvegarder_cookies(contexte, fichier):
    print("on sauvegarde")

    # récupérer storage_state
    state = await contexte.storage_state()

    # sauvegarder formaté
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)

    print("✅ cookies sauvegardés :", fichier)
    
    
    
# NAVIGATION
async def ouvrir_facebook(contexte):
    page = await contexte.new_page()
    await appliquer_stealth(page)
    await page.goto("https://www.facebook.com", timeout=0)
    return page



# PAUSE
async def pause(minutes):
    await asyncio.sleep(minutes * 60)
    

