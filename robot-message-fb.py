import asyncio, random
from datetime import datetime, timedelta
from itertools import cycle
from playwright.async_api import async_playwright

from outils_playwright import (creer_context, creer_page, aller, envoyer_message, charger_json, est_blacklist, ajouter_blacklist, sauvegarder_json)
from db import (profils_a_envoyer, maj_prochain_message, messages_envoyes_aujourdhui, incrementer_message)

FICHIER_BLACKLIST = "sauvegarde-bs/blacklist.json"

def prochaine_date():
    jours = random.randint(90, 120)
    date = datetime.now() + timedelta(days = jours)
    return date.strftime("%Y-%m-%d")

async def visiter(browser, compte, profil, messages, blacklist):
    profil_id, url, name = profil
    fichier = compte["fichier"]
    max_messages = compte.get("max_messages", 20)
    envoyes = messages_envoyes_aujourdhui(fichier)
    if envoyes >= max_messages: print("Limite atteinte :", fichier); return
    if est_blacklist(blacklist, fichier, url): print("Blacklist :", fichier, url); return

    contexte = await creer_context(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        ok = await envoyer_message(page, messages, name, url, fichier)
        if ok:
            date = prochaine_date()
            maj_prochain_message(profil_id, date)
            incrementer_message(fichier)
    except Exception as e:
        print("Erreur :", e)
        ajouter_blacklist(blacklist, FICHIER_BLACKLIST, fichier, url)

    await contexte.close()

async def main():
    comptes = charger_json("accounts-fb.json", [])
    messages = charger_json("phrases-travail.json", [])
    blacklist = charger_json(FICHIER_BLACKLIST, {})
    index_zone = charger_json("index_zone_rm.json", {})
    zone = index_zone.get("start_zone")

    comptes = [c for c in comptes if not c["fichier"].startswith("-")]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False, args = ["--disable-blink-features=AutomationControlled"])
        cycle_comptes = cycle(comptes)

        while True:
            profils = profils_a_envoyer(zone)
            if not profils:
                print("Aucun profil à contacter")
                await asyncio.sleep(300)
                continue

            for profil in profils:
                await visiter(browser, next(cycle_comptes), profil, messages, blacklist)

asyncio.run(main())

