import json
import asyncio
from playwright.async_api import async_playwright


async def save_cookies(context):
    cookies = await context.cookies()
    with open("c-insta-laura.json", "w") as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)
        # json.dump(cookies, f)


async def apply_stealth(page):
    await page.add_init_script(
        """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    """
    )

    # await page.add_init_script(
    #    """
    # Object.defineProperty(navigator, 'webdriver', {get: () => false});
    # Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR', 'fr']});
    # Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
    # """
    # )


def load_cookies(file_path="c-insta-laura.json"):
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



async def creer_compte(page):
    page.get_by_label("Numéro de mobile ou adresse e-mail").fill("gillesilluminati@gmail.com")
    page.get_by_label("Mot de passe").fill("Diel2019@#")
    page.get_by_label("Nom complet").fill("Laura")
    page.get_by_label("Nom de profil").fill("Mercier")
    page.get_by_text("Jour").click()
    page.wait_for_timeout(500) # attendre que les options apparaissent
    page.get_by_text("05").click()
    
    
async def main():
    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False)

        browser = await p.chromium.launch(
            headless=False,
            # executable_path="/usr/bin/google-chrome-stable"  # <-- on force Chrome officiel
            # executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
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
        await page.goto("https://www.instagram.com/accounts/emailsignup/?next=", timeout=0)
        
        #await page.goto("https://www.threads.com/@muriel_blanche/post/DWgXEecjSOz", timeout=0)

        print("on patiente 1 min")
        await asyncio.sleep(60)

        print("on patiente 1 min")
        #await asyncio.sleep(60)

        print("on enregistre les cookies")

        await save_cookies(context)
        print("cookies enregistré")
        
        await creer_compte(page)

        # Remplace time.sleep par asyncio.sleep (non bloquant)
        await asyncio.sleep(10000)


if __name__ == "__main__":
    asyncio.run(main())
