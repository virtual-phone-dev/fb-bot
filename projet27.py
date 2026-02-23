import json, asyncio, random
from playwright.async_api import async_playwright, TimeoutError
from pathlib import Path

DEBUG_CODEGEN = True


async def apply_stealth(page):
    await page.add_init_script(
        """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    """
    )
    
    
async def get_context_and_page(p):
    browser = await p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-web-security",
        ]
    )
    
    context = await browser.new_context()

    # Timeout global pour toutes les actions (clic, saisie, wait_for, etc.)
    context.set_default_timeout(180000) # 7 minutes . click(), fill(), wait_for_selector(), locator.wait_for()
    context.set_default_navigation_timeout(180000) # Timeout global spécifique à la navigation (goto, reload, wait_for_url)

    # Charger les cookies AVANT d'ouvrir la page
    cookies = load_cookies()
    await context.add_cookies(cookies)

    page = await context.new_page()

    # appliquer stealth
    await apply_stealth(page)
    return browser, context, page


async def save_cookies(context):
    cookies = await context.cookies()
    with open("cookies-fb2.json", "w") as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)
        # json.dump(cookies, f)
        
        
def load_cookies(file_path="cookies-fb2.json"):
    with open(file_path, "r", encoding="utf-8") as f:
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
            }
        )
    return cookies


async def publier_post(page):

    # Cliquer sur la zone "Créer une publication"
    publier_box = page.locator("div[aria-label='Créer une publication']").first
    await publier_box.click()

    # Attendre que la zone de texte apparaisse
    zone_texte = page.locator("div[role='textbox']").first
    await zone_texte.fill("super, merci")

    # Cliquer sur le bouton "Publier"
    bouton_publier = page.locator("div[aria-label='Publier']").first
    await bouton_publier.click()

    print("✅ Publication Publier :")


async def main():
    async with async_playwright() as p:
        browser, context, page = await get_context_and_page(p)

        if DEBUG_CODEGEN:
            print("🔎 Mode codegen : pause pour inspector")
            await page.pause()
            return


        #context = await browser.new_context()

        # Timeout global pour toutes les actions (clic, saisie, wait_for, etc.)
        #context.set_default_timeout(180000) # 7 minutes . click(), fill(), wait_for_selector(), locator.wait_for()
        #context.set_default_navigation_timeout(180000) # Timeout global spécifique à la navigation (goto, reload, wait_for_url)

        # Charger les cookies AVANT d'ouvrir la page
        #cookies = load_cookies()
        #await context.add_cookies(cookies)

        #page = await context.new_page()

        # appliquer stealth
        #await apply_stealth(page)

        print("Aller sur la page")
        await page.goto("https://www.facebook.com/profile.php?id=61558927355917")
      
        print("on patiente 6 min")
        #await asyncio.sleep(60)

        print("on patiente 1 min")
        #await asyncio.sleep(60)

        print("on enregistre les cookies")

        #await save_cookies(context)
        print("cookies enregistré")
        
        
        try:
            # Sélecteur CSS ciblant le SVG avec aria-label="Votre profil"
            svg = await page.wait_for_selector('svg[aria-label="Votre profil"]', timeout=60000)
            await svg.click()
            print("SVG cliqué avec succès !")
        except TimeoutError:
            print("Erreur : SVG introuvable ou le chargement a pris trop de temps.")
       
        
        try:
            bouton = await page.wait_for_selector('[aria-label="Basculer sur Maliworikè"]', timeout=60000)
            await bouton.click()
            print("✅ Bouton 'Basculer sur Maliworkè' cliqué avec succès !")
        except TimeoutError:
            print("⏳ Erreur : bouton introuvable (temps dépassé).")
            
            
        try:
            # Cherche l’élément contenant le texte "Que voulez-vous dire"
            #bouton = await page.wait_for_selector('span:has-text("Que voulez-vous dire")', timeout=10000)
            #await bouton.click()
            await page.click('span:has-text("Que voulez-vous dire")')
            print("✅ Zone 'Que voulez-vous dire' cliquée avec succès !")
        except TimeoutError:
            print("⏳ Erreur : zone introuvable (temps dépassé).")
            
        print("publier_post")    
        
        #await publier_post(page)
        print("pret à close")
        
        await asyncio.sleep(100000)

        # await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
