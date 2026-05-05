import json, asyncio, time, msvcrt
from playwright.async_api import async_playwright
from outils_playwright import (connecter_gmail, charger_cookies, sauvegarder_cookies, charger_fichier, basculer_sur_la_page, reparer_fb)

PAUSE_MINUTES = 1


texte = """Dis à tes abonnés de regarder leur vidéos préférées sur Florinato. 
On paye 100 dollars pour 1000 inscriptions, 1000 personnes qui vont s'inscrire avec ton lien, et tu pourras suivre les statistiques des inscriptions sur ton compte Florinato.
Et si jamais tu crées ton compte Florinato, n'oublie pas d'envoyer un message à CAISIP (sur Florinato).

Si ça t'intéresse, voilà ton lien de Partenaire, tu publies ça sur ta page, en disant à tes abonnés de regarder leur vidéos préférées sur Florinato.
https://florinato105.onrender.com """

objet = "Invitation, Mai 2026."




# VERIFIER COMMANDE CONSOLE
async def verifier_commande(page, duree_minutes):
    print("Écrivez..")
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



async def charger_comptes(fichier_des_comptes):
    with open(fichier_des_comptes, "r", encoding="utf-8") as f:
        return json.load(f)
        
        
async def save_cookies(context):
    print("patiente 7s")
    await asyncio.sleep(7)
    
    print("on sauvegarde les cookies")
    cookies = await context.cookies()
    with open(fichier_cookie, "w") as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)

    print("cookies sauvegardé")
    
    

async def apply_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] }); """)


    
async def envoyer_email(page, email):
    btn = await page.query_selector("text=Nouveau message")
    if btn:
        await btn.click()
    print("patiente 3s"); await asyncio.sleep(3)
    
    #await page.fill('input[aria-label="Destinataires"]', 'Ton texte ici')
    await page.locator('input[aria-label="Destinataires"]').fill(email)
    await page.locator('input[aria-label="Objet"]').fill(objet)

    await page.click('div[aria-label="Corps du message"]') #on clique dabord avant d'écrire pour activer la zone de texte, car l'input est en mode contenteditable="true"
    await page.keyboard.type(texte)
    
    print("patiente 2s"); await asyncio.sleep(2)
    #await page.get_by_role("button", name="Envoyer").click() #Cliquer sur le bouton Envoyer

        
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(        
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-web-security",
            ],
        )

        #context = await browser.new_context()
        
        fichier_emails = "mes_emails.json"
        emails = await charger_fichier(fichier_emails)
        emails = [e for e in emails if not str(e.get("fichier", "")).strip().startswith("-")]

        #page = await context.new_page() # nouvel onglet
        #await apply_stealth(page)
        
        for mail in emails:
            
            fichier_cookie = mail["fichier"]
            email = mail["email"]
            nom = mail["nom"]
            print("✅ Compte : ", nom);
            print(email);
            
            context = await browser.new_context() #nouveau contexte pour chaque compte
            
            # Charger les cookies AVANT d'ouvrir la page
            cookies = charger_cookies(fichier_cookie)
            await context.add_cookies(cookies)
        
            #nom_complet = compte["nom_complet"]
            #nom_profil = compte["nom_profil"]
            
            page = await context.new_page()
            await apply_stealth(page)
            
            await connecter_gmail(page, email)
            await envoyer_email(page, email)
            #await verifier_message_fb(page, email, mot_de_passe);
            
            #await verifier_commande(page, PAUSE_MINUTES)
            await sauvegarder_cookies(context, fichier_cookie)
            #await creer_compte_insta(page, context, compte, fichier_des_comptes, email, mot_de_passe)

            #await page.goto("https://www.instagram.com", timeout=0)
            #await connecter_compte_insta(page, context, compte, fichier_des_comptes, email, mot_de_passe, nom_profil)
            
            #await commenter_th(page, email, mot_de_passe)
            #break
            
            #await reparer_th(page, context, nom_complet, email, mot_de_passe)
            
            print("patiente 10000s"); await asyncio.sleep(10000)
            await context.close() #fermer le contexte (ou la fenetre)

if __name__ == "__main__":
    asyncio.run(main())
