import json, asyncio, os, sys, msvcrt, time
import outils_playwright as outils
from playwright.async_api import async_playwright

MODE_SILENCIEUX = True
PAUSE_MINUTES = 1



# Stealth
async def appliquer_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
    Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
    Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
    """
    )


# EXTRAIRE INFOS COMPTE
async def extraire_fichier(compte):
    if isinstance(compte, str):
        fichier = compte
    else:
        fichier = compte["fichier"]

    ignore = fichier.startswith("-")
    return fichier.lstrip("-"), ignore
    


async def preparer_storage_state(fichier):
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
async def verifier_commande(page, duree_minutes):
    await page.goto("https://www.facebook.com",timeout=0)   
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


    
async def creer_page(page, context):  
    try:
        await page.goto("https://www.facebook.com/pages/creation/?ref_type=comet_home", timeout=0)
        #print("Patiente 1s"); await asyncio.sleep(1)
        
        btn = page.locator('span:has-text("Nom de la Page (obligatoire)")')
        if await btn.count() > 0:
            await btn.fill("Richesse avec SATAN")
        
        
        btn = page.get_by_label("Catégorie (obligatoire)") 
        if await btn.count() > 0:
            await page.get_by_label("Catégorie (obligatoire)").fill("reli")    
            print("Patiente 2s"); await asyncio.sleep(1)
        
            await page.evaluate("""
            const span = Array.from(document.querySelectorAll('span')).find(el => el.textContent.trim() === 'Centre religieux');
            if (span) { span.click(); } """)
            
            
        btn = page.locator('span:has-text("Bio (facultatif)")')
        if await btn.count() > 0:
            await btn.fill("Viens faire ton sacrifice pour avoir la Richesse")
            
        
        btn = page.get_by_label("Créer une Page") 
        if await btn.count() > 0:
            await btn.click()
            #print("Patiente 5s"); await asyncio.sleep(5)
            
        while True:    
            element = await page.query_selector("text=Une erreur est survenue lors de la création de la page.")
            if element:
                print("impossible de crée la Page")
                await context.close()
                break
                
            element = await page.query_selector("text=Terminez la configuration de votre Page")
            if element:
                print("Page crée")
                break
               
        debut = time.time()       
        while True:
            btn = page.get_by_label("Suivant")
            if await btn.count() > 0:  
                await btn.click(); 
                print("Suivant 1"); 
                break
                
            if time.time() - debut > 5:
                print("fb.com")
                await page.goto("https://fb.com", timeout=0)
                break
                
                
        while True:
            btn = page.get_by_label("Suivant")
            if await btn.count() > 0:  
                await btn.click(); 
                print("Suivant 2"); 
                break
        
        debut = time.time()
        while True:
            try:
                btn = page.get_by_label("Ignorer")
                if await btn.count() > 0:  
                    await btn.click(); 
                    print("Ignorer"); 
                    break
            except:
                pass
                
            # si 5 secondes dépassées
            if time.time() - debut > 5:
                print("fb.com")
                await page.goto("https://www.facebook.com", timeout=0)
                break
           
           
        while True:
            btn = page.get_by_label("Suivant")
            if await btn.count() > 0:  
                await btn.click(); 
                print("Suivant 3"); 
                
            btn = page.get_by_label("Terminé")
            if await btn.count() > 0:  
                await btn.click(); 
                print("Terminé"); 
                break
                
        print("Patiente 30s"); await asyncio.sleep(30);
    except:
        return 
   

   
async def basculer_sur_la_page(page):
    while True:
        try:
            btn = page.get_by_label("Votre profil")
            if await btn.count() > 0:
                await page.evaluate("""
                const btn = document.querySelector('div[aria-label="Votre profil"]');
                if (btn) { btn.click(); } """)
                
    
            print("patiente 5s"); await asyncio.sleep(5)
            btn = page.get_by_label("Basculer sur")
            if await btn.count() > 0:  
                await btn.click();
                
            element = await page.query_selector("text=Tableau de bord professionnel")
            if element:
                print("Connecté sur la page :")
                print("patiente 3s"); await asyncio.sleep(3)
                await page.goto(url_post, timeout=0) 
                print("patiente 4s"); await asyncio.sleep(4)
                break
        except:
            pass

          
async publier_post(page) :
    await page.goto("https://www.facebook.com", timeout=0)
    await basculer_sur_la_page(page)
    print("Patiente 10000s"); await asyncio.sleep(10000);


          
async def main():
    comptes = json.load(open("comptes-fb.json", encoding="utf-8"))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        total = len(comptes)

        for index, compte in enumerate(comptes):
            fichier, ignore = await extraire_fichier(compte)

            if ignore:
                if not MODE_SILENCIEUX:
                    print("ignoré :", fichier)
                continue

            print(f"\n===== {index+1}/{total} =====")
            print("Compte :", fichier)
            
            await preparer_storage_state(fichier)
            
            context = await browser.new_context(storage_state=fichier)   
            
            page = await context.new_page()
            await appliquer_stealth(page)            
            try:
                #await creer_page(page, context)
                await publier_post(page)
                # await verifier_commande(page, PAUSE_MINUTES)  # si besoin
                # Sauvegarder cookies ou autres si nécessaire
                await outils.sauvegarder_cookies(context, fichier)
            except:
                continue
            finally:
                await context.close()

asyncio.run(main())

