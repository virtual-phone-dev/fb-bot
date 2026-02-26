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


        
async def envoyer_commentairee(page, COMMENTS, posts=None, fichier_posts=None):
    print("on cherche le post puis on clique sur le bouton Commenter")

    # cas 1
    post_comment_button=page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    count_post_comment_button=await post_comment_button.count()
    print("count_post_comment_button",count_post_comment_button)

    if count_post_comment_button>0:
        await post_comment_button.click()
        print("Attente apparition zone commentaire")
        await asyncio.sleep(random.uniform(24,60))

        post=await page.query_selector('[id][data-ad-preview="message"]')

        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)

        await asyncio.sleep(random.uniform(6,12))
        await page.keyboard.press("Enter")

        print("✅ Commentaire envoyé même sans texte du post")
        await asyncio.sleep(random.uniform(24, 30))
        return True
    
    # cas 2
    first_post2=page.locator('[role="article"]').nth(0)
    post_link=await first_post2.locator("a[href*='/posts/'], a[href*='/videos/']").nth(0).get_attribute("href")

    if post_link:
        good_url=post_link.split('?')[0]
        print(f"bb ✅ Lien du post le plus récent : {good_url}")

        if posts and post_deja_commente(posts,good_url):
            print(f"hh 🔄 Post déjà commenté : {good_url}")
            return True

        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        await comment_box.fill(comment)
        await page.keyboard.press("Enter")

        print("Commentaire réussi")
        print(f"Post : {good_url}")
        print(f"Commentaire : {comment}")

        print("gg on sauvegarde le lien du post")
        if posts and fichier_posts: ajouter_post(posts, fichier_posts, good_url)
        print("zz post sauvegarder")

        await asyncio.sleep(random.uniform(24, 30))
        return True

    # cas 3
    print("❌ Aucun selecteur commentaire trouvé (Cas 3 à ajouter)")
    return False
    
    
    
async def envoyer_commentaire(page, COMMENTS, posts=None, fichier_posts=None, commented_posts=None, context=None):
    print("Recherche du post pour commenter...")
    identifiant_post=None; post_link=None

    # CHOIX DU PREMIER POST
    post_comment_button = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first
    count_post_comment_button = await post_comment_button.count()

    if count_post_comment_button > 0:        
        print("Source utilisée : article nth(0)")
        source_post = page.locator('[role="article"]').nth(0)
        print("a00")
    else:
        print("Source utilisée : bouton commentaire")
        source_post = post_comment_button
        print("a0")
    

    # RÉCUPÉRATION LIEN
    link_locator = source_post.locator("a[href*='/posts/'], a[href*='/videos/']")
    count_link = await link_locator.count()
    print("lien compter nombre :", count_link)


    if count_link > 0:
        print("a1")
        post_link = await link_locator.first.get_attribute("href")
        print("a2 lien trouvé :", post_link)
    else:
        post_link = None
        print("a4 aucun lien trouvé")

    if post_link:
        print("a5")
        identifiant_post=post_link.split('?')[0]
        print(f"✅ Lien détecté : {identifiant_post}")

        if posts and post_deja_commente(posts, identifiant_post):
            print(f"🔄 Déjà commenté : {identifiant_post}")
            if context:
                print("a6")
                await page.close(); await context.close()
                print("a7")
            return True

        if posts and fichier_posts:
            print("a8")
            ajouter_post(posts, fichier_posts, identifiant_post)
            print("✅ Lien sauvegardé")

    # SINON TEXTE
    if not identifiant_post:
        try:
            print("a9")
            post=await source_post.locator('[data-ad-preview="message"]').first
            print("a10")
            texte=await post.inner_text()
            print("a11")
            identifiant_post=texte.strip()
            print(f"✅ Texte détecté : {identifiant_post}")

            if commented_posts and identifiant_post in commented_posts:
                print(f"🔄 Déjà commenté : {identifiant_post}")
                if context:
                    print("a12")
                    await page.close(); await context.close()
                    print("a13")
                return True

            if commented_posts is not None:
                print("a14")
                commented_posts.add(identifiant_post)
                print("a15")
                save_commented_posts(commented_posts)
                print("✅ Texte sauvegardé")
        except:
            print("a16")
            pass
            print("a17")

    # CAS 1
    # CAS 1
    if count_post_comment_button > 0:
        print("a18")
        await post_comment_button.click()
        print("Attente apparition zone commentaire")
        await asyncio.sleep(random.uniform(14,30))
        print("a19")

        comment_box=page.locator("div[role='textbox']").first
        print("a20")
        comment=random.choice(COMMENTS)
        print("a21")
        await comment_box.fill(comment)
        print("a22")
        await asyncio.sleep(random.uniform(6,12))
        print("a23")
        await page.keyboard.press("Enter")

        print("✅ Commentaire envoyé (cas 1)")
        print(f"Post : {identifiant_post}")
        print(f"Commentaire : {comment}")

        await asyncio.sleep(random.uniform(24,30))
        print("a24")
        return True

    # CAS 2
    if post_link:
        print("a25")
        comment_box=page.locator("div[role='textbox']").first
        comment=random.choice(COMMENTS)
        print("a26")
        await comment_box.fill(comment)
        print("a27")
        await page.keyboard.press("Enter")

        print("✅ Commentaire envoyé (cas 2)")
        print(f"Post : {identifiant_post}")
        print(f"Commentaire : {comment}")

        await asyncio.sleep(random.uniform(24,30))
        print("a28")
        return True

    # CAS 3
    print("❌ Aucun selecteur commentaire trouvé (Cas 3 à ajouter)")
    return False
    
    