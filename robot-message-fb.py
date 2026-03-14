import asyncio, random
from datetime import datetime, timedelta
from itertools import cycle
from playwright.async_api import async_playwright

from outils_playwright import (creer_context, creer_page, aller, envoyer_message, charger_json, sauvegarder_json)
from db import (profils_a_envoyer, maj_prochain_message, messages_envoyes_aujourdhui, incrementer_message)


def prochaine_date():
    jours = random.randint(90, 120)
    date = datetime.now() + timedelta(days = jours)
    return date.strftime("%Y-%m-%d")


def calculer_prochaine_pause():
    minutes = random.randint(45, 60)
    date = datetime.now() + timedelta(minutes=minutes)
    return date.strftime("%Y-%m-%d %H:%M")
    

def verifier_pause(compte):
    pause = compte.get("pause_prochain_envoi", "")
    if pause == "":
        return True
        
    date_pause = datetime.strptime(pause, "%Y-%m-%d %H:%M")
    return datetime.now() >= date_pause



async def visiter(browser, compte, profil, messages, comptes):
    profil_id, url, name = profil
    fichier = compte["fichier"]
    
    if not verifier_pause(compte):
        print("Compte en pause :", fichier)
        return
    
    max_messages = compte.get("max_messages", 20)
    envoyes = messages_envoyes_aujourdhui(fichier)
    if envoyes >= max_messages: print("Limite atteinte :", fichier); return

    contexte = await creer_context(browser, fichier)
    page = await creer_page(contexte)

    try:
        await aller(page, url)
        ok = await envoyer_message(page, messages, name, url, fichier)
        if ok:
            date = prochaine_date()
            maj_prochain_message(profil_id, date)
            incrementer_message(fichier)
            
            compte["pause_prochain_envoi"] = calculer_prochaine_pause()
            sauvegarder_json("accounts-fb.json", comptes)
    
    except Exception as e:
        print("Erreur :", e)
    await contexte.close()
    
    
async def main():
    comptes = charger_json("accounts-fb.json", [])
    messages = charger_json("phrases-travail.json", [])
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
                await visiter(browser, next(cycle_comptes), profil, messages, comptes)

asyncio.run(main())

