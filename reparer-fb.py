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
async def main():
    comptes = json.load(open("accounts.json", encoding="utf-8"))

    async with async_playwright() as p:
        navigateur = await p.chromium.launch(headless=False)
        total = len(comptes)

        for index, compte in enumerate(comptes):
            fichier, ignore = extraire_fichier(compte)

            if ignore:
                if not MODE_SILENCIEUX:
                    print("ignoré :", fichier)
                continue

            print(f"\n===== {index+1}/{total} =====")
            print("Compte :", fichier)

            contexte = await navigateur.new_context(storage_state=fichier)
            page = await outils.ouvrir_facebook(contexte)

            # print(f"⏳ pause {PAUSE_MINUTES} min")
            # await outils.pause(PAUSE_MINUTES)

            await verifier_commande(PAUSE_MINUTES)
            await outils.sauvegarder_cookies(contexte, fichier)

            await contexte.close()

        await navigateur.close()
        print("\n✅ terminé")

asyncio.run(main())

