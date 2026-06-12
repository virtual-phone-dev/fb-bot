import asyncio, re
from playwright.async_api import async_playwright
from outils_playwright import (charger_fichier_d, verifier_nouveau_element, verifier_date_recontacte, mettre_a_jour, appliquer_stealth, 
charger_cookies, ajouter_dans_fichier, nettoyer_texte, mots_inutiles, domaines_autoriser)

# leav = Liste des experts AMO Vaud . https://www.vd.ch/fileadmin/user_upload/themes/environnement/energie/fichiers_pdf/Liste_AMO_accredites.pdf
# lm = Liste des médiateurs . https://www.cours-appel.justice.fr/sites/default/files/2025-09/CA%20ORLEANS-Liste%20des%20médiateurs-2024-2026.pdf
# lede = Liste des ensigenant departement Électronique . https://fge.usthb.dz/wp-content/uploads/2026/02/Liste-des-enseignants-ELN-5.pdf


url_osteopathe ="https://www.osteopathie.org/?fond=annuaire&nom=&prenom=&cpostal=&ville=&departement=&region=&latlong=&pays=&page={}#results"
url_site_architecte = "https://www.cfai.fr/fr/recherche/annuaire-professionnel?page={}"
url_ordre_avocats = "https://www.ordre-avocats-cassation.fr/annuaire" # oac = ordre-avocats-cassation
url_barreau_marseille = "https://www.barreau-marseille.avocat.fr/fr/annuaire" # bm = barreau marseille
url_barreau_marseille_2 = "https://www.barreau-marseille.avocat.fr/fr/annuaire/page-{}" 


async def site_barreau_marseille(page):
    await parcourir_pages2(page, premiere_url=url_barreau_marseille, url_template=url_barreau_marseille_2, max_pages=1000, domaine="avocat", pays="France", site="bm",
    
    selecteur_lignes = "div.b-annuaire__content",
    selecteur_nom = "div.noms h2",
    selecteur_telephone = 'a[href^="tel:"]',
    selecteur_email = 'a[href^="mailto:"]')
    
    

async def site_avocat1(page):
    await page.goto(url_ordre_avocats, timeout=0)
    await email_site_avocat(page, domaine="avocat", pays="France", site="oac",
    
    selecteur_lignes = "table tbody tr",
    selecteur_nom = "td.views-field.views-field-view-user a",
    selecteur_telephone = "td.views-field.views-field-field-annu-phone-1",
    selecteur_email = '[href^="mailto:"]')



async def email_site_avocat(page, domaine, pays, site, selecteur_lignes, selecteur_nom, selecteur_telephone, selecteur_email):      
    lignes = await page.query_selector_all(selecteur_lignes)   
    
    for ligne in lignes:
        if ligne:
            email_element = await ligne.query_selector(selecteur_email) # recuperer email
            if not email_element: continue
            href = await email_element.get_attribute("href")
            
            if href:
                email = href.replace("mailto:", "").strip()
                
                if email.endswith(domaines_autoriser):
                    print("email :", email);
                    nom, telephone = await recup_nom_telephone(ligne, selecteur_nom, selecteur_telephone)
                    
                    await ajouter_dans_fichier("emails_collecter_europe.json", 
                    { "email": email, "nom": nom, "telephone": telephone, "domaine": domaine, "pays": pays, "site": site }, "email", email)
        

    
async def recup_nom_telephone(page, selecteur_nom, selecteur_telephone):
    element = await page.query_selector(selecteur_telephone)
    if element:
        telephone = await element.inner_text()
    else:
        telephone = ""
    
    
    element = await page.query_selector(selecteur_nom)
    if element:
        nom = await element.inner_text()
        nom = nom.strip(); print(nom); print(telephone);
    else:
        nom = ""
        
    return nom, telephone
    


async def extraire(page):           
    result = await page.evaluate("""
            () => {
                const header = document.querySelector('h5.titre.clearfix');
                if (!header) return { nom: null, numero: null };
                const nom = header.firstChild.textContent.trim();
                const numeroElement = header.querySelector('strong');
                const numero = numeroElement ? numeroElement.textContent.trim() : null;
                return { nom, numero };
            }
        """)
        
    nom = result['nom']
    telephone = result['numero']
    print('Nom:', nom)
    print('Numéro:', telephone)
    
    return nom, telephone


async def cliquer_contact(page, domaine, pays):          
    elements = await page.query_selector_all("table.table.table-striped.table-hover.table-list tbody tr") # Récupère tous les éléments <tr> dans le tbody
    total = len(elements)
    
    for i in range(total):
        elements = await page.query_selector_all("table.table.table-striped.table-hover.table-list tbody tr") # Re-sélectionner les trs à chaque itération (important !)
        element = elements[i]
        
        btn = await element.query_selector("td.table-list-actions a.btn")
        if btn:
            print(f'clic reussi {i + 1}/{total}')
            await btn.click()
            await page.wait_for_load_state("networkidle")
            
            element = await page.query_selector("div.col-inner header h1")
            nom = await element.inner_text(); print(nom);
            await email(page, nom, domaine, pays)
                
            await page.go_back()
            await page.wait_for_load_state("networkidle")
            
            
           
async def email(page, domaine, pays, site):          
    elements = await page.query_selector_all('[href^="mailto:"]') # recuperer email
    
    for element in elements:
        if element:
            href = await element.get_attribute("href")
            
            if href:
                email = href.replace("mailto:", "").strip()
                
                if email.endswith(domaines_autoriser):
                    print("email :", email);
                    
                    await ajouter_dans_fichier("emails_collecter_europe.json", 
                    { "email": email, "nom": nom, "telephone": telephone, "domaine": domaine, "pays": pays, "site": site }, "email", email)
        
                    #nom, telephone = await extraire(page)
                    #await mettre_a_jour("emails_collecter_europe.json", {"nom": nom, "telephone": telephone }, "email", email)


        
async def collecter(page, page_num, url_site, domaine, pays):
    good_url = url_site.format(page_num)
    await page.goto(good_url, timeout=0)
    
    if domaine == "osteopathe":
        await email(page, domaine, pays)
    
    if domaine == "architecte":
        await cliquer_contact(page, domaine, pays)



async def parcourrir_page(page, url_site, domaine, pays, start_page=1, max_pages=100):
    for page_num in range(start_page, max_pages + 1):
        print("page ", page_num)
        await collecter(page, page_num, url_site, domaine, pays)


async def parcourir_pages2(page, premiere_url, url_template, max_pages, **kwargs):
    await page.goto(premiere_url, timeout=0)
    await email_site_avocat(page, **kwargs)

    for page_num in range(1, max_pages + 1):
        await page.goto(url_template.format(page_num), timeout=0)
        await email_site_avocat(page, **kwargs)
        
        lignes = await page.query_selector_all("div.b-annuaire__content") # ce code normalement, cest pour marquer la fin, (genre si ya plus de pages a scraper, il arrete la boucle)
        if len(lignes) == 0: print("fin de pagination"); break
    


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

        try:
            context = await browser.new_context()
            page = await context.new_page()
            await appliquer_stealth(page)     
            
            await site_barreau_marseille(page)
            
            #await site_avocat1(page)
            #await parcourrir_page(page, url_template=url_site_osteopathe, domaine="osteopathe", pays="France", start_page=5, max_pages=100) # Ostéopathes
            #await parcourrir_page(page, url_site=url_site_architecte, domaine="architecte", pays="France", start_page=1, max_pages=600) # architectes
            
            print("patiente 10000s"); await asyncio.sleep(10000)
        except Exception as e:
            print("cc.."); print(e)
        
asyncio.run(main())
