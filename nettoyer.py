import json, asyncio, re
from outils_playwright import (charger_fichier_t, charger_fichier, ajouter_dans_fichier, nettoyer_texte, mots_inutiles, domaines_autoriser, sauvegarder_sur_meme_ligne,
sauvegarder_par_bloc)




async def exporter_numeros_txt():
    fichier_entree = "artistes2.json"
    fichier_sortie = "numeros.txt"
    
    artistes = await charger_fichier(fichier_entree)
    
    lignes_sortie = []
    count = 0
    urls_vues = set()
    
    for item in artistes:
        nom = item.get("nom", "").strip()
        url = item.get("url", "")
        
        numeros = []
        for champ in ["telephone_bio", "telephone_span", "telephone_span_proche_bio"]:
            valeur = item.get(champ)
            if valeur and valeur not in numeros:
                numeros.append(valeur)
        
        if not numeros:
            continue
        
        if url in urls_vues:
            print(f"⚠️ DOUBLON détecté : {nom} ({url})")
        urls_vues.add(url)
        
        lignes_sortie.append(nom)
        lignes_sortie.extend(numeros)
        lignes_sortie.append("")
        count += len(numeros)  # compte chaque numéro, pas chaque artiste
    
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_sortie))
    
    print(f"✅ {count} numéros exportés (artistes uniques: {len(urls_vues)}) dans {fichier_sortie}")
    
    
async def exporter_numeros_txt1():
    fichier_entree = "artistes2.json"
    fichier_sortie = "numeros.txt"
    
    artistes = await charger_fichier(fichier_entree)
    
    lignes_sortie = []
    count = 0
    
    for item in artistes:
        nom = item.get("nom", "").strip()
        
        numeros = []
        for champ in ["telephone_bio", "telephone_span", "telephone_span_proche_bio"]:
            valeur = item.get(champ)
            if valeur and valeur not in numeros:  # évite les doublons (ex: LOUMSA avec 2 numéros différents)
                numeros.append(valeur)
        
        if not numeros:
            continue  # ignore les entrées sans numéro (telephone: 0, ou rien du tout)
        
        lignes_sortie.append(nom)
        lignes_sortie.extend(numeros)
        lignes_sortie.append("")  # ligne vide entre chaque artiste
        count += 1
    
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_sortie))
    
    print(f"✅ {count} artistes avec numéro exportés dans {fichier_sortie}")




async def creer_artistes_json():
    fichier_entree = "fichier.txt"
    fichier_sortie = "fichier.json"
    lignes = await charger_fichier_t(fichier_entree)

    artistes = []
    for ligne in lignes:
        parties = ligne.split(" ", 1)  # coupe au premier espace : url puis le reste
        if len(parties) < 2:
            continue
        url = parties[0].strip()
        nom = parties[1].strip()
        artistes.append({"nom": nom, "url": url})

    await sauvegarder_par_bloc(fichier_sortie, artistes, 5)
    print(f"✅ {len(artistes)} fichiers sauvegardés dans {fichier_sortie}")




async def nettoyer_emails_et_supprimer_champ():
    fichier_entree = "emails_collecter.json"
    fichier_sortie = "emails_nettoyer.json"
    emails = await charger_fichier(fichier_entree)
    
    existant = await charger_fichier(fichier_sortie) or []
    emails_existants = {p.get("email") for p in existant}
    
    count = 0
    for item in emails:
        email = item.get("email", "").strip()
        nom = item.get("nom", "").strip()
        nom_clean = await nettoyer_texte(nom)
        
        if email in emails_existants:
            continue
        if "%" in email or any(mot in nom_clean for mot in mots_inutiles):
            continue
        
        existant.append({"email": email, "nom": nom})
        emails_existants.add(email)
        print(email)
        count += 1
    
    existant.sort(key=lambda x: x.get("nom", "").lower())
    await sauvegarder_sur_meme_ligne(fichier_sortie, existant)
    
    print(f"✅ {count} emails sauvegardés")
    print(f"{len(existant)} emails dans le fichier {fichier_sortie}")   
    
    
    
async def nettoyer_pages_avec_nom_inutile():
    fichier_entree = "page_messages_collecter.json"
    fichier_sortie = "fichier_nettoyer.json"

    pages = await charger_fichier(fichier_entree)
    count = 0

    for page in pages:
        message = page.get("message", "").strip()
        nom = page.get("nom", "").strip()
        
        nom_clean = await nettoyer_texte(nom)

        # ignorer les noms contenant des mots inutiles
        if not any(mot in nom_clean for mot in mots_inutiles):
            await ajouter_dans_fichier(fichier_sortie, { "message": message, "nom": nom }, "message", message, "nom")
            print(message)
            count += 1

    print(f"✅ {count} pages sauvegardées")
    resultat = await charger_fichier(fichier_sortie)
    print(f"{len(resultat)} pages dans le fichier {fichier_sortie}")
    
    

async def nettoyer_emails_avec_nom_inutile():
    fichier_entree = "emails_collecter.json"
    fichier_sortie = "emails_nettoyer.json"    
    emails = await charger_fichier(fichier_entree)

    count = 0
    for item in emails:
        email = item.get("email", "").strip()
        nom = item.get("nom", "").strip()
        
        nom_clean = await nettoyer_texte(nom)

        # garder seulement les emails, dont les noms ne font pas parti de mots_inutiles
        if ("%" not in email and not any(mot in nom_clean for mot in mots_inutiles)):
            await ajouter_dans_fichier(fichier_sortie, { "email": email, "nom": nom }, "email", email, "nom")
            print(email)
            count += 1

    print(f"✅ {count} emails sauvegardés")
    
    resultat = await charger_fichier(fichier_sortie)
    print(f"{len(resultat)} emails dans le fichier {fichier_sortie}")
    
    
    
async def recuperer_nom(): #recuperer le nom de l'email
    fichier_entree = "mes_emails.txt"
    fichier_sortie = "mes_emails.json"
    emails = await charger_fichier_t(fichier_entree)

    for email in emails:
        if email:  
            nom = email.split("@")[0] 
            fichier = f"cookies-gmail/{nom}.json" 

            await ajouter_dans_fichier(fichier_sortie, { "fichier": fichier, "email": email, "nom": nom }, "email", email, "nom")
    
    
    resultat = await charger_fichier(fichier_sortie)
    print(f"{len(resultat)} emails dans le fichier {fichier_sortie}")
    


async def nettoyer_email_trouver_avec_beaucoup_de_champ():
    fichier_entree = "mes_emails.txt"
    fichier_sortie = "emails_collecter_europe.json"
    emails_lignes = await charger_fichier_t(fichier_entree)
    
    # Pattern pour extraire les emails du texte
    pattern_email = r'\b[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    
    for ligne in emails_lignes:
        # Extraire tous les emails de la ligne
        emails_trouves = re.findall(pattern_email, ligne)
        
        for email in emails_trouves:
            if email.endswith(domaines_autoriser):
                nom = email.split("@")[0]
                await ajouter_dans_fichier(fichier_sortie, {"email": email, "nom": nom, "pays": "Algerie", "site": "lede"}, "email", email)
    
    resultat = await charger_fichier(fichier_sortie)
    print(f"{len(resultat)} emails dans le fichier {fichier_sortie}")
    
    
async def nettoyer_email_trouver(): #recuperer le nom de l'email
    fichier_entree = "mes_emails.txt"
    #fichier_sortie = "emails_collecter.json"
    fichier_sortie = "emails_collecter_europe.json"
    emails = await charger_fichier_t(fichier_entree)

    for email in emails:
        if email.endswith(domaines_autoriser):
            nom = email.split("@")[0] 
            await ajouter_dans_fichier(fichier_sortie, {"email": email, "nom": nom, "pays": "Suisse", "site": "leav"}, "email", email, "nom")  
            
    resultat = await charger_fichier(fichier_sortie)
    print(f"{len(resultat)} emails dans le fichier {fichier_sortie}")
    
    
    
async def nettoyer_emails_gmail():
    fichier_entree = "emails_collecter.json"
    fichier_sortie = "emails_nettoyer.json"
    
    emails = await charger_fichier(fichier_entree)

    count = 0
    for item in emails:
        email = item.get("email", "").strip().lower()
        nom = item.get("nom", "").strip()
        
        nom_clean = nom.replace("\xa0", " ") #nettoyer les espaces invisibles

        # garder seulement gmail
        if email.endswith("@gmail.com") and "Compte vérifié" not in nom_clean:
            await ajouter_dans_fichier(fichier_sortie, { "email": email, "nom": nom}, "email", email, "nom")
            print(email)
            count += 1

    print(f"✅ {count} emails sauvegardés")
    resultat = await charger_fichier(fichier_sortie)
    print(f"{len(resultat)} emails dans le fichier {fichier_sortie}")
    
    
    
asyncio.run(exporter_numeros_txt())

