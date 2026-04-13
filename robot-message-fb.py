import asyncio, random, json, sqlite3
from datetime import datetime, timedelta
from itertools import cycle
from playwright.async_api import async_playwright
from datetime import datetime
from outils_playwright import (creer_context, creer_page, aller, charger_json)
#from db import (maj_prochain_message, messages_envoyes_aujourdhui, incrementer_message)

DB = "profils.db"


def connexion(): return sqlite3.connect(DB)


def ajouter_colonne():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Vérifier si la colonne 'raison' existe déjà
    cur.execute("PRAGMA table_info(listeAmis)")
    colonnes = [info[1] for info in cur.fetchall()]

    if 'raison' not in colonnes:
        # Ajouter la colonne 'raison'
        cur.execute("ALTER TABLE listeAmis ADD COLUMN raison TEXT")
        print("Colonne 'raison' ajoutée avec succès.")
    else:
        print("La colonne 'raison' existe déjà.")
    conn.commit(); conn.close()


def ObtenirLien(monCompte):
    conn = connexion()
    cur = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""SELECT id, nomAmis, lienAmis, monCompte FROM listeAmis WHERE monCompte = ? AND (prochain_message IS NULL OR prochain_message <= ?)""", 
        (monCompte, today_str))
    
    data = cur.fetchall()   # 🔥 récupère les données
    conn.close()

    return data
    

def messages_envoyes_aujourdhui(nomFichierCompte):
    conn = connexion(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""SELECT envoyes FROM messages_jour WHERE date = ? AND compte = ?""", (today, nomFichierCompte))
    row = cur.fetchone()
    conn.close()
    if row: return row[0]
    return 0


def verifier_pause(nomFichierCompte, lesPause):
    pause = lesPause.get(nomFichierCompte)
    if not pause:
        return True

    date_pause = datetime.strptime(pause["prochain_envoi"], "%Y-%m-%d %H:%M")
    #return datetime.now() >= date_pause
    return datetime.now() < date_pause 
    
    
async def tous_en_pause(comptes_actifs, lesPause):
    for c in comptes_actifs:        
        #await asyncio.sleep(1)
        nomFichierCompte = c['id_inchangeable'];
        data_lien = ObtenirLien(nomFichierCompte)

        if data_lien:
            #print("Le compte a des amis")
            if verifier_pause(nomFichierCompte, lesPause): print(f"Compte en pause : {nomFichierCompte}"); continue
            else: print(f"Compte actuel : {nomFichierCompte}"); return False
        else: print(f"Aucun ami sur le compte de {nomFichierCompte}")
            
    #print("\n Tous les comptes sont en pause")
    print("\n Tous les comptes sont en pause")
    return True
    
    
def get_prochaine_pause(lesPause):
    dates = []

    for compte, pause in lesPause.items():
        try:
            date_str = pause["prochain_envoi"];
            date_pause = datetime.strptime(date_str, "%Y-%m-%d %H:%M");
            dates.append((date_pause, compte))
        except Exception as e: print(f"Erreur pour {compte} : {e}")

    # Remplace if not dates
    if dates:
        resultat = min(dates, key = lambda x: x[0]); print(f"Prochaine pause : {resultat}")
        return resultat
    else: print("Aucune date valide trouvée"); return None
    
        
# ca sauvegarde manuellement et ne modifies pas ton style dans le fichier json
def sauvegarder_json(fichier, data):
    lignes = []
    for item in data:
        ligne = json.dumps(item, ensure_ascii=False)
        lignes.append("\t" + ligne + ",")

    contenu = "\n".join(lignes)

    with open(fichier, "w", encoding="utf-8") as f:
        f.write(contenu)
        
  
def pause_24h():
    date = datetime.now() + timedelta(hours=24)
    return date.strftime("%Y-%m-%d %H:%M")
  

async def maj_prochain_message(idAmi, date):
    conn = connexion(); cur = conn.cursor()
    cur.execute("UPDATE listeAmis SET prochain_message = ? WHERE id = ?", (date, idAmi))
    conn.commit(); conn.close()

async def incrementer_message(nomFichierCompte):
    conn = connexion(); cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""INSERT INTO messages_jour(date, compte, envoyes) VALUES(?, ?, 1) ON CONFLICT(date, compte) DO UPDATE SET envoyes = envoyes + 1""", (today, nomFichierCompte))
    conn.commit(); conn.close()

  
async def prochaine_date():
    jours = random.randint(90, 120)
    date = datetime.now() + timedelta(days = jours)
    return date.strftime("%Y-%m-%d")

async def calculer_prochain_envoi():
    minutes = random.randint(45, 60)
    date = datetime.now() + timedelta(minutes=minutes)
    return date.strftime("%Y-%m-%d %H:%M")
  
  
async def mettre_a_jour_prochainMessage_et_raison(idAmi):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Calculer la date dans 5 mois
    date_prochain = datetime.now() + timedelta(days=150)
    date_str = date_prochain.strftime("%Y-%m-%d")

    # Mettre à jour 'prochain_message' et 'raison'
    cur.execute("""
        UPDATE listeAmis 
        SET prochain_message = ?, raison = ? 
        WHERE id = ?
    """, (date_str, "attendreConnexionMessenger", idAmi))
    
    conn.commit(); conn.close()



async def envoyer_message(page, contexte, idAmi, phrases, monCompte, nomAmis, lienAmis):
    print("ami :", monCompte); print(nomAmis); print(lienAmis); 
    
    await page.evaluate("""
    const messageButton = document.querySelector('div[aria-label="Message"]'); // cliquer sur le bouton Message, une popup s'ouvre alors , pour ecrire le message
    if (messageButton) { messageButton.click(); }
    """)
    
    print("Patiente 2s"); await asyncio.sleep(2);
    while True:
        element = await page.query_selector("text=ne peut pas encore accéder à cette discussion")
        if element:
            print("❌ Discussion inaccessible")
            await mettre_a_jour_prochainMessage_et_raison(idAmi)
            print("terminé, 05 mois"); await contexte.close(); return


        element = await page.query_selector("text=Vous avez atteint la limite d’invitations par message")
        if element:
            print("❌ limite atteinte"); await contexte.close(); return
        
        
        element = await page.query_selector("text=Ce contenu n’est pas disponible pour le moment")
        if element:
            print("Compte inexistant"); await contexte.close(); return
    
    
        message_box = page.locator('div[aria-label="Écrire un message"]').first
        if await message_box.count() > 0:
            phrase = random.choice(phrases)
            await message_box.fill(phrase)        
            
            print("Patiente 1s"); await asyncio.sleep(1)
            await page.keyboard.press("Enter")

            print("Message envoyé :", phrase);
            print("Patiente 7s"); await asyncio.sleep(7)
            break
            
    #while True:
    #    input_box = page.get_by_placeholder("Nom de profil, numéro de mobile ou e-mail")
    #    if await input_box.count() > 0:            
    #        await input_box.fill(email)
    #        break
            
            
            
async def visiter(browser, nomFichierCookie, nomFichierCompte, ami, phrases, lesPause):
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
        await envoyer_message(page, contexte, idAmi, phrases, monCompte, nomAmis, lienAmis)
        #print("Patiente 10000s"); await asyncio.sleep(10000)
                
        #resultat = await envoyer_message(page, phrase, nomAmis, lienAmis, monCompte)
        #identifiant = compte["id_inchangeable"]

        # limite facebook
        #if resultat == "limite":
        #    lesPause[nomFichierCompte] = { "prochain_envoi": pause_24h(), "limite": "Oui" }

        #    with open("pause_prochain_envoi.json", "w", encoding = "utf-8") as f: 
        #        json.dump(lesPause, f, ensure_ascii = False, indent = 2)
        #    print("Compte bloqué 24h :", nomFichierCompte)
        #    return
            
        date = await prochaine_date(); 
        await maj_prochain_message(idAmi, date); await incrementer_message(nomFichierCompte)

        lesPause[nomFichierCompte] = { "prochain_envoi": await calculer_prochain_envoi(), "limite": "" }
        with open("pause_prochain_envoi.json", "w", encoding = "utf-8") as f: 
            json.dump(lesPause, f, ensure_ascii = False, indent = 2)
            
    except Exception as e:
        print("Erreur :", e)        
    finally:
        await contexte.close()
    
    
async def main():
    #ajouter_colonne()
    #print("Patiente 5000s"); await asyncio.sleep(5000)
    
    comptes = charger_json("comptes-fb.json", []); 
    phrases = charger_json("phrase-pret.json", []); 
    lesPause = charger_json("pause_prochain_envoi.json", {}); 
    index_zone = charger_json("index_zone_rm.json", {})
    
    comptes_actifs = [c for c in comptes if not c["fichier"].startswith("-")]
    cycle_comptes = cycle(comptes_actifs)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False, args = ["--disable-blink-features=AutomationControlled"])

        while True:
            # Vérifier si tous les comptes avec amis sont en pause
            if await tous_en_pause(comptes_actifs, lesPause):
                prochaine_pause = get_prochaine_pause(lesPause)
                if prochaine_pause:
                    date_pause, compte_associe = prochaine_pause
                    maintenant = datetime.now()
                    delta = (date_pause - maintenant).total_seconds()
                    if delta > 0:
                        print(f"Tous les comptes avec amis en pause. En pause jusqu'à {date_pause}. Attente de {delta} secondes.")
                        await asyncio.sleep(delta)
                    else:
                        print("La pause est déjà passée, on continue")
                continue  # Recommencer la boucle après la pause
                
            #print("Pause terminé")
            #await asyncio.sleep(10)
            
        
            for compte in comptes_actifs:
                nomFichierCompte = compte['id_inchangeable'] 
                nomFichierCookie = compte['fichier'] 
                data_lien = ObtenirLien(nomFichierCompte)
                
                #if not verifier_pause(nomFichierCompte, lesPause):
                #    print("Compte en pause :", nomFichierCompte)
                #    continue
                
                if not data_lien:
                    print(f"Aucun ami sur le compte de {nomFichierCompte}")
                    continue
                
                # Si tu veux traiter uniquement le premier contact filtré
                ami = data_lien[0]
                await visiter(browser, nomFichierCookie, nomFichierCompte, ami, phrases, lesPause)
                
            await asyncio.sleep(15)   
            
asyncio.run(main())
