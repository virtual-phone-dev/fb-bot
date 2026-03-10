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

# Ouvrir bs
async def ouvrir_bs(contexte):
    page = await contexte.new_page()
    await appliquer_stealth(page)
    await page.goto("https://bsky.app/",timeout=0)
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
    await page.wait_for_load_state("networkidle")


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



async def envoyer_commentaire_bs(page, COMMENTS, posts=None, fichier_posts=None, page_name=None, page_url=None, cookie_file=None):
    identifiant_post = None

    # 🔹 trouver le premier post
    post_locator = page.locator('div[data-testid="contentHider-post"]').first
    count_post = await post_locator.count()

    if count_post == 0:
        print("❌ Aucun post trouvé")
        return False

    # 🔹 récupérer texte du post
    try:
        texte = await post_locator.text_content() or ""
        identifiant_post = " ".join(texte.split())[:500]
        print("Texte :", identifiant_post[:80])

        # vérifier déjà commenté
        if posts and post_deja_commente(posts, identifiant_post):
            print("Déjà commenté")
            return True

        # sauvegarder texte
        if posts is not None and fichier_posts:
            ajouter_post(posts, fichier_posts, identifiant_post)

    except Exception as e:
        print("Erreur récupération texte :", e)
        return False


    # 🔹 cliquer sur le post
    await page.evaluate("""
    const posts = document.querySelectorAll('div[data-testid="contentHider-post"]');
    if (posts.length > 0) {
      posts[0].click();
    } """)
    await asyncio.sleep(random.uniform(5, 7))


    # 🔹 cliquer sur le bouton Repondre ou rédiger réponse
    await page.evaluate("""
    const buttonRédiger = document.querySelector('button[aria-label="Rédiger une réponse"]');
    if (buttonRédiger) {
      buttonRédiger.click();
    } """)
    await asyncio.sleep(random.uniform(5, 7))
    
    # attendre apparition zone texte
    await page.wait_for_selector("div[role='textbox']", timeout=10000)

    # écrire le commentaire
    comment_box = page.locator("div[role='textbox']").first
    comment = random.choice(COMMENTS)
    await comment_box.fill(comment)
    await asyncio.sleep(random.uniform(4, 6))

    # publier
    await page.evaluate("""
    const boutonPublier = document.querySelector('button[aria-label="Publier la réponse"]');
    if (boutonPublier) {
      boutonPublier.click();
    } """)
    
    print("✅ Commentaire envoyé :", comment)
    print(cookie_file)
    print(page_name)
    print(page_url)
        
    await asyncio.sleep(random.uniform(10, 15))
    return True
    
    
    

        
async def envoyer_commentaire(page, COMMENTS, posts=None, fichier_posts=None, page_name=None, page_url=None, cookie_file=None, commented_posts=None, context=None):
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
        source_post = post_comment_button
    else:
        source_post = page.locator('[role="article"]').nth(0)
        
    
    # RÉCUPÉRATION TEXTE POST (NOUVELLE MÉTHODE)
    try:        
        post_element = page.locator('[data-ad-rendering-role="story_message"]').first
        texte = await post_element.text_content()
        
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

    if count_link > 0:
        post_link = await link_locator.first.get_attribute("href")
        print("lien trouvé :", post_link)
    else:
        post_link = None
   

    # CAS 1
    if count_post_comment_button > 0:
        await post_comment_button.click()
        print("Attente apparition zone commentaire")
        await asyncio.sleep(random.uniform(5, 8))

        # CLIQUER SUR "RÉPONDRE"
        await page.evaluate(""" 
        const btn = Array.from(document.querySelectorAll('button, [role="button"]'))
          .find(b => b.innerText.trim() === 'Répondre');
        if (btn) btn.click(); 
        """);
        
        await asyncio.sleep(random.uniform(5, 8))

        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)
        await asyncio.sleep(random.uniform(4, 6))
        await page.keyboard.press("Enter")
        
        print(f"✅ Commentaire envoyé : {comment}")
        print(f"{page_name}")
        print(f"{page_url}")     
        print(f"{cookie_file}")
        
        await asyncio.sleep(random.uniform(20, 25))
        return True
        

    # CAS 2
    if post_link:
        # CLIQUER SUR "RÉPONDRE"
        await page.evaluate(""" 
        const btn = Array.from(document.querySelectorAll('button, [role="button"]'))
          .find(b => b.innerText.trim() === 'Répondre');
        if (btn) btn.click(); 
        """);

        await asyncio.sleep(random.uniform(4, 6))
    
        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)
        await page.keyboard.press("Enter")
        
        print("Cas 2")
        print(f"✅ Commentaire envoyé : {comment}")
        print(f"{page_name}")
        print(f"{page_url}")
        print(f"{cookie_file}")
        
        await asyncio.sleep(random.uniform(20, 25))
        return True


    # CAS 3
    print("❌ Aucun selecteur commentaire trouvé (Cas 3 à ajouter)")
    return False
    
    
