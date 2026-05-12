import json, asyncio
from outils_playwright import (charger_fichier_t, charger_fichier, ajouter_dans_fichier, nettoyer_texte, mots_inutiles)

    

async def nettoyer_emails_avec_nom_inutile():
    fichier_entree = "emails_collecter.json"
    fichier_sortie = "emails_nettoyer.json"    
    emails = await charger_fichier(fichier_entree)

    count = 0
    for item in emails:
        email = item.get("email", "").strip().lower()
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
            await ajouter_dans_fichier(fichier_sortie, { "email": email, "nom": nom }, "email", email, "nom")
            print(email)
            count += 1


    print(f"✅ {count} emails sauvegardés")
    
    resultat = await charger_fichier(fichier_sortie)
    print(f"{len(resultat)} emails dans le fichier {fichier_sortie}")
    
    
asyncio.run(nettoyer_emails_avec_nom_inutile())
