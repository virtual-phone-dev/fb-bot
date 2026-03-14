import asyncio
from playwright.async_api import async_playwright
from outils_playwright import creer_context, creer_page, goto_with_domcontentloaded, charger_json, collecter_liens

async def visiter(browser, compte):
    fichier = compte["fichier"]; lien = compte["lienCompte"]; zone = compte["id_inchangeable"]
    contexte = await creer_context(browser, fichier); page = await creer_page(contexte)
    await goto_with_domcontentloaded(page, lien)
    print("Collecte amis pour :", zone)
    await collecter_liens(page, zone)

async def main():
    comptes = charger_json("accounts-fb.json", [])
    comptes = [c for c in comptes if not c["fichier"].startswith("-")]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False, args = ["--disable-blink-features=AutomationControlled"])
        for compte in comptes: await visiter(browser, compte)

asyncio.run(main())
