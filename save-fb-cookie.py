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
        await page.goto("https://www.facebook.com", timeout=0)

        print("on patiente 3 min")
        await asyncio.sleep(60 * 3)

        print("on enregistre les cookies")
        await context.storage_state(path="cookies-fb2.json")  # sauvegarde cookies + session
        print("cookies enregistrés")
        
        await asyncio.sleep(10000)
        #await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
