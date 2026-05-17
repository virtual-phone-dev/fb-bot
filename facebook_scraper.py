import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from outils_playwright import (charger_fichier, charger_fichier_d, sauvegarder_sur_meme_ligne, sauvegarder_fichier, charger_cookies, apply_stealth, verifier_date_recontacte, verifier_nouveau_element)

format_date = "%Y-%m-%d %H:%M:%S"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
    count = 0
    while count < 2:
        comptes = await verifier_nouveau_element("", "", "fichier")
        comptes = [c for c in comptes if not str(c.get("fichier", "")).strip().startswith("-")]
        for compte in comptes:
            context = await browser.new_context()
            cookies = charger_cookies(compte.get("fichier"))
            await context.add_cookies(cookies)
            page = await context.new_page()
            await apply_stealth(page)
            data_mot = await charger_fichier_d("")
            mot_debut = data_mot.get("mot_cle")
            mots = await charger_fichier("")
            start_index = mots.index(mot_debut) if mot_debut in mots else 0
            for i in range(start_index, len(mots)):
                mot = mots[i]
                mot_suivant = mots[i+1] if i+1 < len(mots) else ""
                print(f"🔍 Recherche en cours : {mot}")
                try:
                    await asyncio.sleep(1)
                    input_box = page.get_by_placeholder("")
                    if await input_box.count() > 0:
                        await input_box.fill(mot)
                        await input_box.press("Enter")
                except Exception as e:
                    print("Erreur recherche:", e)
                await sauvegarder_fichier("", { "mot_cle": mot_suivant })
        count += 1
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())