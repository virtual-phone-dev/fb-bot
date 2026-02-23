from playwright.async_api import async_playwright
import asyncio, json, random, itertools, sys, traceback, requests


# 👉 ton API Node.js Socket.IO
API_URL = "https://api-robot-6u54.onrender.com/"  


def send_log(message, level="INFO"):
    try:
        requests.post(API_URL, json={"message": message, "level": level}, timeout=2)
    except Exception:
        pass


# Redéfinir print pour envoyer aussi les logs
def log_print(*args, **kwargs):
    message = " ".join(str(a) for a in args)
    send_log(message, level="INFO")
    builtins_print(*args, **kwargs)  # garde l’affichage normal dans la console


# Sauvegarder le vrai print
import builtins
builtins_print = builtins.print
builtins.print = log_print


# Capture des erreurs globales
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    send_log(error_msg, level="ERROR")
    builtins_print(error_msg)

sys.excepthook = handle_exception



async def apply_stealth(page):
    await page.add_init_script(
        """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    """
    )


# Charger la liste des comptes
with open("accounts.json", "r", encoding="utf-8") as f:
    ACCOUNTS = json.load(f)

# Charger la liste des pages
with open("pages-speed-congo.json", "r", encoding="utf-8") as f:
    PAGES = json.load(f)
#URLS = [p["url"] for p in PAGES] # Extraire directement les URL


# Charger la liste des commentaires
with open("comments-lien.json", "r", encoding="utf-8") as f:
    COMMENTS = json.load(f)

# commentaires avec le premier mot dupliquer
with open("comments-lien2.json", "r", encoding="utf-8") as f:
    COMMENTS2 = json.load(f)


JSON_FILE_COMMENTED_POSTS = "commented_posts.json"

# Charger la blacklist si elle existe déjà
try:
    with open("blacklist.json", "r", encoding="utf-8") as f:
        BLACKLIST = set(json.load(f))
except:
    BLACKLIST = set()

# Pages en erreur (à retenter)
ERREURS = {}

# Fonction pour charger les posts déjà commentés
def load_commented_posts():
    try:
        with open(JSON_FILE_COMMENTED_POSTS, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

# Fonction pour sauvegarder les posts commentés
def save_commented_posts(posts_set):
    with open(JSON_FILE_COMMENTED_POSTS, "w", encoding="utf-8") as f:
        json.dump(list(posts_set), f, ensure_ascii=False, indent=2)

# Charger les cookies
async def load_cookies(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)
    cookies = []
    for c in raw_cookies:
        cookies.append({
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "expires": c.get("expirationDate", -1)
        })
    return cookies



async def visiter_page(browser, account, url, commented_posts):
    
    context = await browser.new_context()

    # Timeout global pour toutes les actions (clic, saisie, wait_for, etc.)
    context.set_default_timeout(180000)  # 7 minutes . click(), fill(), wait_for_selector(), locator.wait_for()
    context.set_default_navigation_timeout(180000) # Timeout global spécifique à la navigation (goto, reload, wait_for_url)

    try:
        cookies = await load_cookies(account)
        await context.add_cookies(cookies)

        page = await context.new_page()

        # appliquer stealth
        await apply_stealth(page)

        print("on va sur le site")
        
        #await page.goto(url)
        await page.goto("https://www.facebook.com/romeo242pageofficielle")

        # Cliquer sur le bouton "Commenter"
        await page.click('[aria-label="Laissez un commentaire"]');
        
        print("on cherche le post puis on clique sur le bouton Commenter")
        post_comment_button = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first

        count_post_comment_button = await post_comment_button.count()
        print("count_post_comment_button", count_post_comment_button)

        if post_comment_button:
            await post_comment_button.click()

            print("Attendre que la zone de texte apparaisse après le clic")
            await asyncio.sleep(random.uniform(0.4, 1) * 60)


            # Essayer de récupérer l'élément par id
            post = await page.query_selector('[id][data-ad-preview="message"]') 

            if post:
                texte = await post.inner_text()
                texte_du_post = texte.strip()
                print("dd ✅ texte_du_post le plus récent :", texte_du_post)

                # Vérifier si le post a déjà été commenté
                if texte_du_post in commented_posts:
                    print(f"ee 🔄 Post déjà commenté : {texte_du_post}")
                    await page.close()
                    await context.close()
                    return True 

                # Commentaire avec COMMENTS2
                comment2 = random.choice(COMMENTS2)
                print("88")
                await post_comment_button.type(comment2)
                print("5")
                await asyncio.sleep(random.uniform(0.1, 0.2) * 60)
                print("On envoie le commentaire")
                await page.keyboard.press("Enter")
                print("Commentaire envoyé")

                # Ajouter le post à la liste des posts commentés
                print("kk on sauvegarde le texte du post")
                commented_posts.add(texte_du_post)
                save_commented_posts(commented_posts)
                print("nn post sauvegarder")
                await asyncio.sleep(random.uniform(0.1, 0.2) * 60)
            else:
                print("cc Aucun texte trouvé avec data-ad-preview='message'")

            # Récupérer le lien du post (fait dans tous les cas)
            first_post2 = page.locator('[role="article"]').nth(0)
            post_link = await first_post2.locator("a[href*='/posts/'], a[href*='/videos/']").nth(0).get_attribute("href")

            if post_link:
                good_url = post_link.split('?')[0]
                print("bb ✅ Lien du post le plus récent :", good_url)

                # Vérifier si le post a déjà été commenté
                if good_url in commented_posts:
                    print(f"hh 🔄 Post déjà commenté : {good_url}")
                    await page.close()
                    await context.close()
                    return True
                
                # Zone de commentaire
                comment_box = page.locator("div[role='textbox']").first
                comment = random.choice(COMMENTS)
                await comment_box.fill(comment)                     
                await page.keyboard.press("Enter")
                print("Commentaire réussi")
                print(f"Page : {url}")
                print(f"Post : {good_url}")
                print(f"Compte : {account}")
                print("Commentaire :")
                print(f"{comment}")

                # Ajouter le post à la liste des posts commentés
                print("gg on sauvegarde le lien du post")
                commented_posts.add(good_url)
                save_commented_posts(commented_posts)
                print("zz post sauvegarder")

                await asyncio.sleep(random.uniform(0.1, 0.2) * 60)
                await page.close()
                await context.close()
                return True
            else:
                print("aa Aucun lien trouvé pour le post le plus récent")
                await asyncio.sleep(random.uniform(0.1, 0.2) * 60)
                await page.close()
                await context.close()
                return True
                
    
            # (Bloc redondant — à supprimer ou masqué)
            # C’est du code inaccessible dans la plupart des chemins ; 
            # garder ou nettoyer pour clarté.
            
            comment2 = random.choice(COMMENTS2)
            print("88")
            await post_comment_button.type(comment2)
            print("5")
            await asyncio.sleep(random.uniform(0.1, 0.2) * 60)
            print("on envoie le commentaire")
            await page.keyboard.press("Enter")
            print("commentaire envoyé")
            print("pause..")
            await asyncio.sleep(random.uniform(0.1, 0.2) * 60)
            print("pause terminé")


            first_post2 = page.locator('[role="article"]').nth(0)

            # Récupérer le lien du post
            post_link = await first_post2.locator("a[href*='/posts/'], a[href*='/videos/']").nth(0).get_attribute("href")
            #post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/'], a[href*='/groups/'], a[href*='story.php'], a[href*='/watch/']").first.get_attribute("href")
            good_url = post_link.split('?')[0]
            print("Lien du post le plus récent :", good_url)
            
        await page.mouse.wheel(0, 600)   # Descend de 2000 pixels
        await page.wait_for_timeout(1500) # Attente pour laisser charger
        first_post = page.locator('[role="article"]').nth(0)
        await first_post.wait_for(timeout=30000)  # 10 minutes max d’attente
        await first_post.scroll_into_view_if_needed()

        count_first_post = await first_post.count()
        print("posts trouvées :", count_first_post)

        # Récupérer le lien du post
        post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/']").nth(0).get_attribute("href")
        #post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/'], a[href*='/groups/'], a[href*='story.php'], a[href*='/watch/']").first.get_attribute("href")
        good_url = post_link.split('?')[0]
        print("Lien du post le plus récent :", good_url)

        # Vérifier si le post a déjà été commenté
        if good_url in commented_posts:
            print(f"🔄 Post déjà commenté : {good_url}")
            await page.close()
            await context.close()
            return True  # On considère comme "réussi" puisque déjà commenté
        
        #        return False


        # zone de commentaire
        comment_box = page.locator("div[role='textbox']").first
        #comment_box = first_post.locator("div[role='textbox'][contenteditable='true']").first
        #comment_box = first_post.locator("div[aria-label*='Commenter']").first

        comment = random.choice(COMMENTS)
        await comment_box.fill(comment)                     
        #await asyncio.sleep(random.uniform(0.1, 0.3) * 60)
        await page.keyboard.press("Enter")
        print("Commentaire réussi")
        print(f"page : {url}")
        print(f"post : {good_url}")
        print(f"compte : {account} ")
        print("Commentaire :")
        print(f"{comment}")

        # Ajouter le post à la liste des posts commentés
        commented_posts.add(good_url)
        save_commented_posts(commented_posts)

        await asyncio.sleep(random.uniform(0.3, 1) * 60)

        await page.close()
        await context.close()
        return True

    except Exception as e:
        print("Erreur sur une page")
        print(f"{e}")
        print(f"page : {url}")
        print(f"compte : {account} ")
        await context.close()
        return False

async def main():
    commented_posts = load_commented_posts()

    async with async_playwright() as p:
        #await ensure_browser()

        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-web-security",
            ],
        )

        pages_cycle = itertools.cycle(PAGES)
        compteur = 0  # pages parcourues

        while True:  # boucle infinie
            for account in ACCOUNTS:
                #url = next(pages_cycle)
                page_obj = next(pages_cycle)
                url = page_obj["url"]  # 🔹 on récupère une fois

                # ignorer blacklist
                if url in BLACKLIST:
                    print(f"🚫 {url} est dans la blacklist → ignoré")
                    continue

                ok = await visiter_page(browser, account, url, commented_posts)

                if not ok:
                    # Initialiser la liste des comptes qui ont échoué
                    if url not in ERREURS:
                        ERREURS[url] = {"comptes_tentes": []}
                    ERREURS[url]["comptes_tentes"].append(account)

                    # Si tous les comptes ont échoué → blacklist
                    if len(ERREURS[url]["comptes_tentes"]) == len(ACCOUNTS):
                        print(f"⚠️ {url} a échoué avec tous les comptes → blacklisté")
                        BLACKLIST.add(url)
                        with open("blacklist.json", "w", encoding="utf-8") as f:
                            json.dump(list(BLACKLIST), f, indent=2)
                        del ERREURS[url]

            # Retenter les pages en erreur toutes les 3 cycles
            if compteur % 3 == 0 and ERREURS:
                print("🔄 Retente les pages échouées...")
                for failed_url, infos in list(ERREURS.items()):
                    for acc in ACCOUNTS:
                        if acc not in infos["comptes_tentes"]:
                            ok = await visiter_page(browser, acc, failed_url, commented_posts)
                            if ok:
                                print(f"✅ Succès en réessayant {failed_url} avec {acc}")
                                del ERREURS[failed_url]
                                break
                            else:
                                infos["comptes_tentes"].append(acc)
                                if len(infos["comptes_tentes"]) == len(ACCOUNTS):
                                    print(f"⚠️ {failed_url} encore raté avec tous les comptes → blacklist")
                                    BLACKLIST.add(failed_url)
                                    with open("blacklist.json", "w", encoding="utf-8") as f:
                                        json.dump(list(BLACKLIST), f, indent=2)
                                    del ERREURS[failed_url]

                compteur += 1
                #print("⏳ Fin de cycle → pause 1 min")
                #await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())