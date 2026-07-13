import json, asyncio, os, sys, msvcrt, time
import outils_playwright as outils
from playwright.async_api import async_playwright
from outils_playwright import (sauvegarder_cookies, verifier_commande, appliquer_stealth, preparer_storage_state, extraire_fichier, basculer_sur_le_compte)

MODE_SILENCIEUX = True


async def visiter_page(page, url_page):  
    await page.goto("https://www.facebook.com", timeout=0)
    await basculer_sur_le_compte(page, url_page)
    

async def main():       
    async with async_playwright() as p:
        browser = await p.chromium.launch(        
        headless=False, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars", "--disable-web-security"])
        
        comptes = json.load(open("mes_comptes_fb2.json", encoding="utf-8"))
        comptes = [c for c in comptes if c.get("visiter_compte") == 1]
        #comptes = [c for c in comptes if c.get("message") == 1]
        total = len(comptes)
        url_page = "https://www.facebook.com/profile.php?id=61591692635517"
        
        for index, compte in enumerate(comptes):
            fichier, ignore = await extraire_fichier(compte)
            if ignore:
                if not MODE_SILENCIEUX: print("ignoré :", fichier)
                continue
                
            print(f"\n===== {index+1}/{total} =====")
            print("Compte :", fichier)
            
            await preparer_storage_state(fichier)
            
            context = await browser.new_context(storage_state=fichier)   
            page = await context.new_page()
            await appliquer_stealth(page)            
            await visiter_page(page, url_page)
            await verifier_commande(page, 5)
            
            await sauvegarder_cookies(context, fichier)
            await context.close()

asyncio.run(main())
