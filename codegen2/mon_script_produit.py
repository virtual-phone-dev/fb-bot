# -*- coding: utf-8 -*-
import json, asyncio, time, msvcrt
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from outils_playwright import *

format_date = "%d-%m-%Y"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars", "--disable-web-security"])
        fichier1 = "page_messages.json"
        fichier2 = "page_messages2.json"
        pages_fb = await verifier_nouveau_element(fichier1, fichier2, "message")
        pages_fb = [p for p in pages_fb if await verifier_date_recontacte(p)]

        fichier3 = "mes_comptes_fb.json"
        fichier4 = "mes_comptes_fb2.json"
        comptes_fb = await verifier_nouveau_element(fichier3, fichier4, "message")
        comptes_fb = [c for c in comptes_fb if await verifier_date_recontacte(c) and c.get("message") == 1]

        fichier_page_message_debut = "fichier_page_message_debut.json"
        page_message_debut = (await charger_fichier_d(fichier_page_message_debut)).get("message")

        index = next((i for i, page in enumerate(pages_fb) if page["message"] == page_message_debut), 0)
        page_suivant = None
        pages_deja_contacter = set()
        tour = 0

        if len(comptes_fb) == 0:
            print("Tout les comptes ont été utilisés")
        for compte_fb in comptes_fb:
            tour += 1
            # Configuration de sécurité standard Playwright
            context = await browser.new_context(viewport={"width": 1280, "height": 720})
            await apply_stealth(context)
            page = await context.new_page()

        await browser.close()

asyncio.run(main())
