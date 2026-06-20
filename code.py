import json, asyncio, os, sys, msvcrt, time
from playwright.async_api import async_playwright
from outils_playwright import (connecter_gmail, appliquer_stealth, charger_fichier, ajouter_dans_fichier, connexion_bs, query_selector_text, query_selector_a_text, 
connexion_tu, div_data_testid, div_data_pagelet, button_id, button_button_text, button_submit_text, input_name, input_type, input_id, span_has_text)



async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars", "--disable-web-security"])
            
            context = await browser.new_context()
            page_tu = await context.new_page(); await appliquer_stealth(page_tu)
            
            await connexion_tu(page_tu) # tumblr
        except Exception as e:
            print("..erreur"); print(e)
        
        p=50000; print(f"patiente {p}s"); await asyncio.sleep(p)
        
asyncio.run(main())

