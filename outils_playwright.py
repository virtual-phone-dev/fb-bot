
import json, os, asyncio

# Stealth
async def appliquer_stealth(page):
    await page.add_init_script(
        """
Object.defineProperty(navigator,'webdriver',{get:()=>undefined});
Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
"""
    )

# Charger cookies
def charger_cookies(fichier):
    if not os.path.exists(fichier):
        return []

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            raw_cookies = data.get("cookies", [])
        elif isinstance(data, list):
            raw_cookies = data
        else:
            return []

    except:
        return []

    cookies = []
    for c in raw_cookies:
        if not isinstance(c, dict):
            continue

        cookies.append({
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "expires": c.get("expirationDate", -1),
        })
    return cookies
    
    
# Sauvegarder cookies
async def sauvegarder_cookies(contexte, fichier):
    print("on sauvegarde")
    state = await contexte.storage_state()
    with open(fichier,"w",encoding="utf-8") as f:
        json.dump(state,f,indent=4,ensure_ascii=False)
    print("✅ cookies sauvegardés :", fichier)

# Ouvrir Facebook
async def ouvrir_facebook(contexte):
    page = await contexte.new_page()
    await appliquer_stealth(page)
    await page.goto("https://www.facebook.com",timeout=0)
    return page

# Pause en minutes
async def pause(minutes):
    await asyncio.sleep(minutes*60)

# Injecter cookies
async def injecter_cookies(contexte, fichier):
    cookies = charger_cookies(fichier)
    await contexte.add_cookies(cookies)

# Créer contexte
async def creer_contexte(browser, cookie_file):
    contexte = await browser.new_context()
    contexte.set_default_timeout(180000)
    contexte.set_default_navigation_timeout(180000)
    await injecter_cookies(contexte,cookie_file)
    return contexte

# Créer page
async def creer_page(contexte):
    page = await contexte.new_page()
    await appliquer_stealth(page)
    return page

# Aller vers URL
async def aller(page, url):
    await page.goto(url)


# Pause aléatoire en secondes
async def pause_random(min, max):
    import random
    await asyncio.sleep(random.uniform(min,max))


# JSON utils (du 2e code, sans duplication avec cookies)
def charger_json(fichier, defaut):
    dossier = os.path.dirname(fichier)
    if dossier and not os.path.exists(dossier):
        os.makedirs(dossier)

    if not os.path.exists(fichier):
        with open(fichier,"w",encoding="utf-8") as f:
            json.dump(defaut,f,indent=2)
        return defaut

    with open(fichier,"r",encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return defaut


def sauvegarder_json(fichier, data):
    with open(fichier,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Posts commentés
def post_deja_commente(posts, post):
    return post in posts

def ajouter_post(posts, fichier, post):
    if post not in posts:
        posts.append(post)
        sauvegarder_json(fichier, posts)
        

# Blacklist
def est_blacklist(blacklist, compte, page):
    return compte in blacklist and page in blacklist[compte]
    

def ajouter_blacklist(blacklist, fichier, compte, page):
    if compte not in blacklist:
        blacklist[compte] = []
        
    if page not in blacklist[compte]:
        blacklist[compte].append(page)
        sauvegarder_json(fichier, blacklist)


# facebook
async def trouver_post(page):
    post=page.locator("[role='article']").first
    await post.wait_for(timeout=30000)
    await post.scroll_into_view_if_needed()
    return post

async def trouver_lien_post(post):
    lien=await post.locator("a[href*='/posts/'], a[href*='/videos/']").first.get_attribute("href")
    if lien: lien=lien.split("?")[0]
    return lien

async def ouvrir_commentaire(post,page):
    bouton=post.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    if await bouton.count()>0:
        await bouton.click()
        await page.wait_for_timeout(3000)

async def envoyer_commentaire(page,texte):
    box=page.locator("div[role='textbox']").first
    await box.wait_for(state="visible", timeout=30000)
    await box.click()
    await box.fill(texte)
    await page.keyboard.press("Enter")
    
    