import asyncio, random, json, sqlite3
from datetime import datetime, timedelta
from itertools import cycle
from playwright.async_api import async_playwright
from datetime import datetime
from outils_playwright import (creer_context, creer_page, aller, envoyer_message, charger_json)
from db import (maj_prochain_message, messages_envoyes_aujourdhui, incrementer_message)

DB = "profils.db"


def connexion(): return sqlite3.connect(DB)


def ObtenirLien(monCompte):
    conn = connexion()
    cur = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    cur.execute(
        """SELECT id, nomAmis, lienAmis, monCompte FROM listeAmis WHERE monCompte = ? AND (prochain_message IS NULL OR prochain_message <= ?)""", 
        (monCompte, today_str)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def maj_prochain_message(idAmi, date):
    conn = connexion(); cur = conn.cursor()
    cur.execute("UPDATE listeAmis SET prochain_message = ? WHERE id = ?", (date, idAmi))
    conn.commit(); conn.close()

def messages_envoyes_aujourdhui(nomFichierCompte):
    conn = connexion(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""SELECT envoyes FROM messages_jour WHERE date = ? AND compte = ?""", (today, nomFichierCompte))
    row = cur.fetchone()
    conn.close()
    if row: return row[0]
    return 0

def incrementer_message(nomFichierCompte):
    conn = connexion(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""INSERT INTO messages_jour(date, compte, envoyes) VALUES(?, ?, 1) ON CONFLICT(date, compte) DO UPDATE SET envoyes = envoyes + 1""", (today, nomFichierCompte))
    conn.commit(); conn.close()
	
	
# ca sauvegarde manuellement et ne modifies pas ton style dans le fichier json
def sauvegarder_json(fichier, data):
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


def calculer_prochain_envoi():
    minutes = random.randint(45, 60)
    date = datetime.now() + timedelta(minutes=minutes)
    return date.strftime("%Y-%m-%d %H:%M")
  
  
def pause_24h():
    date = datetime.now() + timedelta(hours=24)
    return date.strftime("%Y-%m-%d %H:%M")
    
    
def verifier_pause(nomFichierCompte, lesPause):
    #identifiant = compte["id_inchangeable"]
    pause = lesPause.get(nomFichierCompte)
    if not pause:
        return True

    date_pause = datetime.strptime(pause["prochain_envoi"], "%Y-%m-%d %H:%M")
    return datetime.now() >= date_pause


async def visiter(browser, nomFichierCookie, nomFichierCompte, ami, phrase, lesPause):
    idAmi, nomAmis, lienAmis, monCompte = ami
    #fichier = compte["fichier"]
    
    #if not verifier_pause(nomFichierCompte, lesPause):
    #    print("Compte en pause :", nomFichierCompte)
    #    return
    
    #max_messages = compte.get("max_messages", 20)
    #envoyes = messages_envoyes_aujourdhui(nomFichierCompte)
    #if envoyes >= max_messages: print("Limite atteinte :", nomFichierCompte); return

    contexte = await creer_context(browser, nomFichierCookie)
    page = await creer_page(contexte)

    try:
        await aller(page, lienAmis)
        resultat = await envoyer_message(page, phrase, nomAmis, lienAmis, monCompte)
        #identifiant = compte["id_inchangeable"]

        # limite facebook
        #if resultat == "limite":
        #    lesPause[nomFichierCompte] = { "prochain_envoi": pause_24h(), "limite": "Oui" }

        #    with open("pause_prochain_envoi.json", "w", encoding = "utf-8") as f: 
        #        json.dump(lesPause, f, ensure_ascii = False, indent = 2)
        #    print("Compte bloqué 24h :", nomFichierCompte)
        #    return
            
        if resultat == "ok":
            date = prochaine_date(); 
            maj_prochain_message(idAmi, date); incrementer_message(nomFichierCompte)

            lesPause[nomFichierCompte] = { "prochain_envoi": calculer_prochain_envoi(), "limite": "" }
            with open("pause_prochain_envoi.json", "w", encoding = "utf-8") as f: 
                json.dump(lesPause, f, ensure_ascii = False, indent = 2)
    except Exception as e:
        print("Erreur :", e)
        
    await contexte.close()
    
    
    
async def main():
    comptes = charger_json("accounts-fb.json", []); 
    phrase = charger_json("phrases-travail.json", []); 
    lesPause = charger_json("pause_prochain_envoi.json", {}); 
    index_zone = charger_json("index_zone_rm.json", {})
    
    comptes_actifs = [c for c in comptes if not c["fichier"].startswith("-")]
    cycle_comptes = cycle(comptes_actifs)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False, args = ["--disable-blink-features=AutomationControlled"])

        while True:
            for compte in comptes_actifs:
                nomFichierCompte = compte['id_inchangeable'] 
                nomFichierCookie = compte['fichier'] 
                data_lien = ObtenirLien(nomFichierCompte)
                
                if not verifier_pause(nomFichierCompte, lesPause):
                    print("Compte en pause :", nomFichierCompte)
                    continue
    
                if not data_lien:
                    print(f"Aucun ami sur le compte de {nomFichierCompte}")
                    continue
                
                # Si tu veux traiter uniquement le premier contact filtré
                ami = data_lien[0]
                await visiter(browser, nomFichierCookie, nomFichierCompte, ami, phrase, lesPause)
                
            #zone = index_zone.get("start_zone")
            #liens = profils_a_envoyer(zone)
            #if not liens: print("Aucun lien à acceder"); continue

            #for lien in liens:
            #    compte = next(cycle_comptes)
            #    index_zone["start_zone"] = compte["id_inchangeable"] # sauvegarder quel compte travaille

            #    with open("index_zone_rm.json", "w", encoding = "utf-8") as f: 
            #        json.dump(index_zone, f, ensure_ascii = False, indent = 2)
                    
            #    await visiter(browser, compte, lien, messages, comptes, pauses)
                
asyncio.run(main())

