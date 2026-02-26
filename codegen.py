import json, asyncio, os, sys, msvcrt, time
import outils_playwright as outils
from playwright.async_api import async_playwright

MODE_SILENCIEUX = True
PAUSE_MINUTES = 1


# EXTRAIRE INFOS COMPTE
def extraire_fichier(compte):
    if isinstance(compte, str):
        fichier = compte
    else:
        fichier = compte["fichier"]

    ignore = fichier.startswith("-")
    return fichier.lstrip("-"), ignore
    


def preparer_storage_state(fichier):
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
async def verifier_commande(duree_minutes):
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
    
    
    
# MAIN
COOKIE_FILE = "cookies-fb/c-karel.json"


async def main():
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
            storage_state=COOKIE_FILE
        )

        page = await context.new_page()

        await page.goto("https://facebook.com")

        print("Codegen prêt. Appuie sur Entrée pour fermer.")
        input()

asyncio.run(main())

asyncio.run(main())

