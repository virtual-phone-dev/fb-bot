import json, asyncio
from playwright.async_api import async_playwright


async def save_cookies(context):
    print("patiente 7s")
    await asyncio.sleep(7)
    
    print("on sauvegarde les cookies")
    cookies = await context.cookies()
    with open("c-th-laura.json", "w") as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)

    print("cookies sauvegardé")
    
    

async def apply_stealth(page):
    await page.add_init_script(
    """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] }); """)



def load_cookies(file_path="c-th-laura.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)

    cookies = []
    for c in raw_cookies:
        cookies.append(
            {
                "name": c.get("name"),
                "value": c.get("value"),
                "domain": c.get("domain"),
                "path": c.get("path", "/"),
                "httpOnly": c.get("httpOnly", False),
                "secure": c.get("secure", False),
                "expires": c.get("expirationDate", -1),
            }
        )
    return cookies



async def creer_compte_threads(page):
    print("on va sur threads")
    await page.goto("https://www.threads.com/@muriel_blanche", timeout=0)
    
    print("patiente 2s")
    await asyncio.sleep(2)  
    await page.evaluate(""" // cliquer sur le bouton Continuer avec Instagram pour afficher mon compte Instagram
    const bouton = Array.from(document.querySelectorAll('span')).find(btn => btn.innerText.includes("Continuer avec Instagram"));
    if (bouton) { bouton.click(); } """)
    
    
    print("patiente 7s")
    await asyncio.sleep(7) 
    print("f1")
    await page.evaluate(""" // cliquer sur mon compte instagram, puis ca va me connecter à mon compte threads
    const btn = document.querySelector('div[role="button"]');
    if (btn) { btn.click(); } """)
    print("f2")
    
    
    
async def connecter(page):
    await page.get_by_label("Numéro de mobile, nom de profil ou adresse e-mail").fill("membrerdc001@gmail.com")
    await page.get_by_label("Mot de passe").fill("Diel2019@#")
    await page.locator('div[aria-label="Se connecter"]').click()
    
    print("patiente 5s")
    await asyncio.sleep(5)
    #await page.wait_for_load_state("load")
    
    #btn = page.get_by_role("button", name="Enregistrer les identifiants")
    #if await btn.count() > 0:
    #    await btn.click()
        
    await creer_compte_threads(page)
    
    
    
async def creer_compte(page):
    await page.get_by_label("Numéro de mobile ou adresse e-mail").fill("membrerdc001@gmail.com")
    await page.get_by_label("Mot de passe").fill("Diel2019@#")
    await page.get_by_label("Nom complet").fill("Laura")
    await page.get_by_label("Nom de profil").fill("Laura_Mercier5")
    
    # selectionner le jour
    await page.evaluate(''' [...document.querySelectorAll("div, span")].find(el => el.textContent.trim() === "Jour").click(); ''')
    await page.wait_for_timeout(100)
    await page.evaluate(''' [...document.querySelectorAll('[role="option"]')].find(el => el.textContent.trim() === "1").click(); ''')
    
    await page.locator('div[aria-label="Sélectionnez le mois"]').click()
    await page.get_by_role("option", name="janvier").click()
    
    # selectionner l'année
    await page.evaluate(''' [...document.querySelectorAll("div, span")].find(el => el.textContent.trim() === "Année").click(); ''')
    await page.wait_for_timeout(100)
    await page.evaluate(''' [...document.querySelectorAll('[role="option"]')].find(el => el.textContent.trim() === "2000").click(); ''')
    
    await page.locator('div[role="button"]', has_text="Envoyer").click()



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

        context = await browser.new_context()

        # Charger les cookies AVANT d'ouvrir la page
        #cookies = load_cookies()
        #await context.add_cookies(cookies)

        page = await context.new_page()

        # appliquer stealth
        await apply_stealth(page)

        print("on va sur le site")
        #await page.goto("https://threads.com", timeout=0)
        await page.goto("https://www.instagram.com", timeout=0)
        #await page.goto("https://www.instagram.com/accounts/emailsignup/?next=", timeout=0)
        
        #await creer_compte(page)
        await connecter(page)
        await save_cookies(context)

        await asyncio.sleep(10000)


if __name__ == "__main__":
    asyncio.run(main())
