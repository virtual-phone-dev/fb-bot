# -*- coding: utf-8 -*-
# Code généré automatiquement via Codegen Studio Universel
import asyncio
from playwright.async_api import async_playwright
from outils_playwright import apply_stealth, verifier_nouveau_element

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

        fichier1 = "sourceA.json"
        fichier2 = "sourceB.json"
        elements = await verifier_nouveau_element(fichier1, fichier2, "id")
        elements = [e for e in elements if await verifier_date_recontacte(e)]
        fichier3 = "sourceA.json"
        fichier4 = "sourceB.json"
        elements = await verifier_nouveau_element(fichier3, fichier4, "id")
        elements = [e for e in elements if await verifier_date_recontacte(e)]

if __name__ == '__main__':
    asyncio.run(main())
