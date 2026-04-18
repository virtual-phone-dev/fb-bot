import json, asyncio, os, sys, msvcrt, time
from playwright.async_api import async_playwright
from outils_playwright import (sauvegarder_cookies)

MODE_SILENCIEUX = True
PAUSE_MINUTES = 1



# Stealth
async def appliquer_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
    Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
    Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
    """
    )


# EXTRAIRE INFOS COMPTE
async def extraire_fichier(compte):
    if isinstance(compte, str):
        fichier = compte
    else:
        fichier = compte["fichier"]

    ignore = fichier.startswith("-")
    return fichier.lstrip("-"), ignore
    


async def preparer_storage_state(fichier):
    dossier = os.path.dirname(fichier)
    if dossier:
        os.makedirs(dossier, exist_ok=True)

    if not os.path.exists(fichier):
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump({
                "cookies": [],
                "origins": []
            }, f, indent=4)
            
            

# VERIFIER COMMANDE CONSOLE
async def verifier_commande(page, duree_minutes):
    await page.goto("https://www.facebook.com",timeout=0)   
    secondes = duree_minutes * 60
    debut = time.time()

    while time.time() - debut < secondes:
        if msvcrt.kbhit():
            cmd = input().strip().lower()

            # passer au compte suivant immédiatement
            if cmd == "+":
                print("compte suivant")
                return

            # pause
            if cmd in ["stop", "-"]:
                print("PAUSE")

                while True:
                    cmd = input("Tape + pour continuer : ").strip()
                    if cmd == "+":
                        print("reprise")
                        debut = time.time()
                        break

        await asyncio.sleep(0.2)
    print("suivant automatique")
    
            
            
async def main():
    comptes = json.load(open("comptes-fb.json", encoding="utf-8"))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        total = len(comptes)

        for index, compte in enumerate(comptes):
            fichier, ignore = await extraire_fichier(compte)

            if ignore:
                if not MODE_SILENCIEUX:
                    print("ignoré :", fichier)
                continue

            print(f"\n===== {index+1}/{total} =====")
            print("Compte :", fichier)
            
            await preparer_storage_state(fichier)
            context = await browser.new_context(storage_state=fichier)   
            
            page = await context.new_page()
            await appliquer_stealth(page)
            
            #await creer_page(page)            
            await verifier_commande(page, PAUSE_MINUTES)
            
            await sauvegarder_cookies(context, fichier)
            await context.close()

        await context.close()
        print("\n✅ terminé")

asyncio.run(main())

