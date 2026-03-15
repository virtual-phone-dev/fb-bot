import asyncio, random, json
from datetime import datetime, timedelta
from itertools import cycle
from playwright.async_api import async_playwright

from outils_playwright import (creer_context, creer_page, aller, envoyer_message, charger_json)
from db import (profils_a_envoyer, maj_prochain_message, messages_envoyes_aujourdhui, incrementer_message)


# ca sauvegarde manuellement et ne modifies pas ton style dans le fichier json
def sauvegarder_json(fichier, data):
    import json

    lignes = []
    for item in data:
        ligne = json.dumps(item, ensure_ascii=False)
        lignes.append("\t" + ligne + ",")

    contenu = "\n".join(lignes)

    with open(fichier, "w", encoding="utf-8") as f:
        f.write(contenu)
        
        
def prochaine_date():
    jours = random.randint(90, 120)
    date = datetime.now() + timedelta(days = jours)
    return date.strftime("%Y-%m-%d")


def calculer_prochaine_pause():
    minutes = random.randint(45, 60)
    date = datetime.now() + timedelta(minutes=minutes)
    return date.strftime("%Y-%m-%d %H:%M")
  
  
def verifier_pause(compte, pauses):
    identifiant = compte["id_inchangeable"]
    pause = pauses.get(identifiant)
    if not pause:
        return True

    date_pause = datetime.strptime(pause, "%Y-%m-%d %H:%M")
    return datetime.now() >= date_pause



async def visiter(browser, compte, profil, messages, comptes, pauses):
    profil_id, url, name = profil
    fichier = compte["fichier"]
    
    if not verifier_pause(compte, pauses):
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

            identifiant = compte["id_inchangeable"]
            pauses[identifiant] = calculer_prochaine_pause()
            sauvegarder_json("pause_prochain_envoi.json", pauses) 
    
    except Exception as e:
        print("Erreur :", e)
        
    await contexte.close()
    
    
    
async def main():
    comptes = charger_json("accounts-fb.json", []); 
    messages = charger_json("phrases-travail.json", []); 
    pauses = charger_json("pause_prochain_envoi.json", {}); 
    index_zone = charger_json("index_zone_rm.json", {})
    
    comptes_actifs = [c for c in comptes if not c["fichier"].startswith("-")]
    cycle_comptes = cycle(comptes_actifs)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False, args = ["--disable-blink-features=AutomationControlled"])

        while True:
            profils = profils_a_envoyer()
            if not profils: print("Aucun profil à contacter"); continue

            for profil in profils:
                compte = next(cycle_comptes)
                index_zone["start_zone"] = compte["id_inchangeable"] # sauvegarder quel compte travaille

                with open("index_zone_rm.json", "w", encoding = "utf-8") as f: 
                    json.dump(index_zone, f, ensure_ascii = False, indent = 2)
                    
                await visiter(browser, compte, profil, messages, comptes, pauses)
                
asyncio.run(main())

