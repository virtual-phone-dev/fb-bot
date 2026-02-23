import json
import asyncio
from playwright.async_api import async_playwright


async def apply_stealth(page):
    await page.add_init_script(
        """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    """
    )


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
                "expires": c.get("expirationDate", -1),
            }
        )
    return cookies


async def main():
    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False)

        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-web-security",
            ],
        )

        context = await browser.new_context()

        # Charger les cookies AVANT d'ouvrir la page
        cookies = load_cookies()
        await context.add_cookies(cookies)
        
        page = await context.new_page()

        # appliquer stealth
        await apply_stealth(page)
        
        
        print("on va sur le site")
        try:
            await page.goto("https://www.facebook.com/profile.php?id=61558927355917", timeout=0)
        except TimeoutError:
            print("⏳ Erreur : le site ne s'est pas chargé correctement")
            await page.screenshot(path="error_1_site.png")

        # Cliquez sur "Votre profil"
        try:
            profil_btn = page.get_by_role("button", name="Votre profil", exact=True)
            await profil_btn.click()
            print("✅ Bouton 'Votre profil' cliqué avec succès")
        except TimeoutError:
            print("⏳ Erreur : bouton 'Votre profil' introuvable")
            await page.screenshot(path="error_2_profil.png")

        # Cliquez sur "Basculer sur Maliworikè"
        try:
            switch_btn = page.get_by_role("button", name="Basculer sur Maliworikè")
            await switch_btn.click()
            print("✅ Bouton 'Basculer sur Maliworikè' cliqué avec succès")
        except TimeoutError:
            print("⏳ Erreur : bouton 'Basculer sur Maliworikè' introuvable")
            await page.screenshot(path="error_3_switch.png")

        # Cliquez sur "Que voulez-vous dire ?"
        try:
            post_box = page.get_by_role("button", name="Que voulez-vous dire ?")
            await post_box.click()
            print("✅ Zone 'Que voulez-vous dire ?' cliquée avec succès")
        except TimeoutError:
            print("⏳ Erreur : zone 'Que voulez-vous dire ?' introuvable")
            await page.screenshot(path="error_4_postbox.png")
            
        # Remplir la zone de texte
        try:
            textbox = page.get_by_role("textbox")
            #await textbox.click()
            await textbox.fill("ça marche, cool")
            print("✅ Zone de texte remplie avec succès")
        except TimeoutError:
            print("⏳ Erreur : zone de texte introuvable")
            await page.screenshot(path="error_5_textbox.png")

        # Cliquer sur "Suivant"
        try:
            next_btn = page.get_by_role("button", name="Suivant")
            await next_btn.click()
            print("✅ Bouton 'Suivant' cliqué avec succès")
        except TimeoutError:
            print("⏳ Erreur : bouton 'Suivant' introuvable")
            await page.screenshot(path="error_6_next.png")

        # Cliquer sur "Publier"
        try:
            publier_btn = page.get_by_role("button", name="Publier", exact=True)
            await publier_btn.click()
            print("✅ Bouton 'Publier' cliqué avec succès")
        except TimeoutError:
            print("⏳ Erreur : bouton 'Publier' introuvable")
            await page.screenshot(path="error_7_publier.png")

        print("🎉 Script terminé")
        
        await asyncio.sleep(60)

        #print("on patiente 6 min")
        #await asyncio.sleep(360)

        #print("on patiente 1 min")
        #await asyncio.sleep(60)

        #print("on enregistre les cookies")

        #await save_cookies(context)
        #print("cookies enregistré")

        # Remplace time.sleep par asyncio.sleep (non bloquant)
        await asyncio.sleep(10000)


if __name__ == "__main__":
    asyncio.run(main())
