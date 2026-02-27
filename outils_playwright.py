import json, os, asyncio, random


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
    await asyncio.sleep(minutes * 60)


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


    
async def creer_context(browser, cookie_file):
    contexte = await browser.new_context(storage_state=cookie_file)
    contexte.set_default_timeout(180000)
    contexte.set_default_navigation_timeout(180000)
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
            data = json.load(f)

            if not isinstance(data, type(defaut)):
                return defaut
            return data
        except:
            return defaut
            
            
def sauvegarder_json(fichier, data):
    with open(fichier,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Posts commentés
def post_deja_commente(posts, lien):
    if not lien:
        return False

    return lien in posts
        
    
def ajouter_post(posts, fichier, lien):
    if lien not in posts:
        posts.append(lien)
        sauvegarder_json(fichier, posts)
        
       
# Blacklist
def est_blacklist(blacklist, compte, page):
    return compte in blacklist and page in blacklist[compte]
    

def ajouter_blacklist(blacklist, fichier, compte, page):
    if compte not in blacklist or not isinstance(blacklist[compte], list):
        blacklist[compte] = []

    if page not in blacklist[compte]:
        blacklist[compte].append(page)
        sauvegarder_json(fichier, blacklist)

    
    
async def envoyer_commentaire(page, COMMENTS, posts=None, fichier_posts=None, commented_posts=None, context=None):
    identifiant_post=None; post_link=None
    
    # 🔹 Vérification indisponibilité
    try:
        indisponible = await page.evaluate('''() => { return document.body.innerText.includes("Ce contenu n’est pas disponible pour le moment") }''')
        if indisponible:
            print("❌ Page indisponible, fermeture du navigateur")
            if context:
                await page.close()
                await context.close()
            return False
    except:
        pass
        
    # CHOIX DU PREMIER POST
    post_comment_button = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    count_post_comment_button = await post_comment_button.count()

    if count_post_comment_button > 0:        
        #print("Source: bouton commentaire")
        source_post = post_comment_button
    else:
        print("Source: article nth(0)")
        source_post = page.locator('[role="article"]').nth(0)
        
    
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:
        #print("Recherche texte du post")
        
        post_element = page.locator('[data-ad-rendering-role="story_message"]').first
        #print("b1")
        texte = await post_element.text_content()
        #texte = await post_element.inner_text()
        
        # 🔥 ICI on coupe à 500 caractères
        identifiant_post = " ".join(texte.split())[:500]
        print(f"Texte : {identifiant_post[:80]}")

        # Vérification déjà commenté
        if posts and post_deja_commente(posts, identifiant_post):
            #print(f"Déjà commenté")

            if context:
                await page.close()
                await context.close()

            return True

        # Sauvegarde texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post)
            #print("Texte sauvegardé")

    except Exception as e:
        print("Impossible de récupérer le texte :", e)
        return False
        
        
    # RÉCUPÉRATION LIEN
    link_locator = source_post.locator("a[href*='/posts/'], a[href*='/videos/']")
    count_link = await link_locator.count()
    #print("lien compter nombre :", count_link)

    if count_link > 0:
        #print("a1")
        post_link = await link_locator.first.get_attribute("href")
        print("lien trouvé :", post_link)
    else:
        post_link = None
        #print("a4 aucun lien trouvé")
   

    # CAS 1
    # CAS 1
    if count_post_comment_button > 0:
        await post_comment_button.click()
        print("Attente apparition zone commentaire")
        await asyncio.sleep(random.uniform(10, 15))

        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)
        await asyncio.sleep(random.uniform(4, 6))
        await page.keyboard.press("Enter")

        print(f"✅ Commentaire envoyé : {comment}")

        await asyncio.sleep(random.uniform(10, 15))
        return True

    # CAS 2
    if post_link:
        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)
        await page.keyboard.press("Enter")

        print("✅ Commentaire envoyé (cas 2)")
        #print(f"Post : {identifiant_post}")
        print(f"✅ Commentaire réussi : {comment}")
        await asyncio.sleep(random.uniform(10, 15))
        return True

    # CAS 3
    print("❌ Aucun selecteur commentaire trouvé (Cas 3 à ajouter)")
    return False
    
    