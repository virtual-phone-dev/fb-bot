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
    await page.goto("https://www.facebook.com/pages/creation/?ref_type=comet_home", timeout=0)
    print("Patiente 4s"); await asyncio.sleep(4)
    
    btn = page.locator('span:has-text("Nom de la Page (obligatoire)")')
    if await btn.count() > 0:
        await btn.fill("Richesse avec SATAN")
    
    
    btn = page.get_by_label("Catégorie (obligatoire)") 
    if await btn.count() > 0:
        await page.get_by_label("Catégorie (obligatoire)").fill("reli")    
        print("Patiente 2s"); await asyncio.sleep(2)
    
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
           
           
    while True:
        btn = page.get_by_label("Suivant")
        if await btn.count() > 0:  
            await btn.click(); 
            break
                
                
    while True:
        try:            
            #print("patiente 5s"); await asyncio.sleep(5)
            btn = page.get_by_label("Suivant")
            if await btn.count() > 0:  
                await btn.click(); 
                
            btn = page.get_by_label("Ignorer")
            if await btn.count() > 0:  
                await btn.click(); 
                break
        except:
            pass     
            
            
    while True:
        btn = page.get_by_label("Suivant")
        if await btn.count() > 0:  
            await btn.click(); 
            
        btn = page.get_by_label("Terminé")
        if await btn.count() > 0:  
            await btn.click(); 
            break
            
    print("Patiente 10000s"); await asyncio.sleep(10000)   
    #try:
    #    btn = page.get_by_label("Menu Facebook")
    #    if await btn.count() > 0:
    #        await btn.click()
    #except:
    #    pass 
            
            
            
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
            
            await creer_page(page, context)            
            
            #await verifier_commande(page, PAUSE_MINUTES)
            
            
            await outils.sauvegarder_cookies(contexte, fichier)
            await context.close()

        await context.close()
        print("\n✅ terminé")

asyncio.run(main())

