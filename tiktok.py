
import json
import asyncio
from playwright.async_api import async_playwright

def load_cookies(file_path="cookies10.json"):
    with open(file_path, "r", encoding="utf-8") as f:
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

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # Charger les cookies AVANT d'ouvrir la page
        cookies = load_cookies()
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto("https://tiktok.com", timeout=0)

        await asyncio.sleep(10000)  

if __name__ == "__main__":
    asyncio.run(main())
