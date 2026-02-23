#cliquer sur le bouton "Modifier le profil"

from playwright.sync_api import sync_playwright
import json

def load_cookies(file_path="cookies.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)

    cookies = []
    for c in raw_cookies:
        # Normalisation stricte du sameSite
        samesite = c.get("sameSite", "").capitalize()
        if samesite not in ["Strict", "Lax", "None"]:
            samesite = "Lax"  # valeur par défaut sûre

        cookies.append({
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "expires": c.get("expirationDate", -1),
            # Normalisation du sameSite
            "sameSite": samesite
        })
    return cookies

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    # Charger les cookies AVANT d'ouvrir la page
    cookies = load_cookies()
    context.add_cookies(cookies)

    page = context.new_page()
    page.goto("https://facebook.com/me", timeout=0)

    # cherche et clique sur le bouton "Modifier le profil"
    # Privilégier les attributs stables : aria-label, data-testid, role plutôt que juste div ou span
    # Cibler par attribut aria-label (plus précis)
    page.locator('[aria-label="Modifier le profil"]').click()
    print(f"click reussie")

    input("Appuie sur Entrée pour fermer...")
    browser.close()
