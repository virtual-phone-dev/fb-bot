import json
import asyncio
import random
from playwright.async_api import async_playwright, TimeoutError


async def apply_stealth(page):
    await page.add_init_script(
        """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    """
    )


def load_cookies(file_path="cookies2.json"):
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
            }
        )
    return cookies


async def jaime(page):
        
        # Liste des sélecteurs possibles
        selectors = [
            # Cas 1 : aria-label
            '[aria-label="J’aime"][role="button"]',
            # Cas 2 : data-ad-rendering-role
            'span[data-ad-rendering-role="j’aime_button"]',
            # Cas 3 : variation où c’est dans un <div>
            'div[aria-label="J’aime"][role="button"]'
        ]

        for i, selector in enumerate(selectors, start=1):
            try:
                buttons = page.locator(selector)
                count = await buttons.count()
                print(f"Cas {i}: trouvé {count} bouton(s)")

                if count > 0:
                    # Récupérer le plus récent (souvent le premier dans le DOM)
                    recent_button = await buttons.first
                    print(f"-> Bouton du post le plus récent détecté pour cas {i}")
                    
                    # Exemple : cliquer dessus
                    recent_button.click()
                    print("clique sur j'aime")
            except Exception as e:
                print(f"Cas {i}: erreur {e}")


async def commenter(page):
    try:
        # Cliquer sur le bouton "Commenter"
        print("on cherche le post puis on clique sur le bouton Commenter")
        post_comment_button = page.locator('div[aria-label="Laissez un commentaire"][role="button"]').first

        count_post_comment_button = await post_comment_button.count()
        print("count_post_comment_button", count_post_comment_button)
        #await post_comment_button.scroll_into_view_if_needed()

        if post_comment_button:
            await post_comment_button.click()

            print("post et bouton trouvé, on click, puis on patiente quelques secondes")
            await asyncio.sleep(random.uniform(0.4, 1) * 60)
            print("on écrit le commentaire")
            await post_comment_button.type("super mariusca")
            await asyncio.sleep(random.uniform(0.2, 4) * 60)
            print("on envoie")
            await page.keyboard.press("Enter")
            print("1commentaire réussi")


            # Exemple Python Playwright
            #publication_text = "Publication de"
            #print("on cherche Publication de")
            #comment_box = page.locator(f'xpath=//span[contains(text(), "{publication_text}")]/ancestor::div[contains(@class, "x1n2onr6")]//div[@contenteditable="true"]')
            #await comment_box.click()
            #await comment_box.fill("2 Ton commentaire ici")
            #print("2 commentaire réussi")

            # Récupérer le lien du post
            post_link = (await post_comment_button.locator("a[href*='/posts/'], a[href*='/videos/']").nth(2).get_attribute("href"))
            # post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/'], a[href*='/groups/'], a[href*='story.php'], a[href*='/watch/']").first.get_attribute("href")
            if post_link:
                good_url = post_link.split("?")[0]
                print("Lien du post le plus récent :", good_url)
            else:
                print("pas de lien trouvé")
        else:
            print("Bouton 'Commenter' introuvable")
            return

        # zone de commentaire
        print("on localise la zone de commentaire")

        

        # comment_box = page.locator("div[role='textbox']").first
        # comment_box = first_post.locator("div[role='textbox'][contenteditable='true']").first
        # comment_box = page.locator("div[aria-label*='Commenter en tant que']").first
        # comments = await page.query_selector_all('div[role="textbox"][contenteditable="true"][aria-label*="Commenter en tant que"]')

        # Clique dans la zone de commentaire
        # comment_box1 = post_comment_button.locator('div[role="textbox"][contenteditable="true"][aria-label*="Commenter en tant que"]').first
        comment_box = page.locator('div[role="textbox"][contenteditapble="true"]').nth(2)
        await comment_box.click()

        # count_comment_box1 = await comment_box1.count()
        count_comment_box = await comment_box.count()
        # print("count_comment_box1", count_comment_box1)
        print("count_comment_box", count_comment_box)

        # Tape ton commentaire
        await page.keyboard.type("on est ensemble")

        # Envoie le commentaire (souvent Enter suffit)
        await page.keyboard.press("Enter")

        # print("on a écrit, on patiente quelques secondes")
        # await asyncio.sleep(random.uniform(0.1, 0.3) * 60)

        print("✅ Commentaire envoyé, on patiente quelques secondes")
        await asyncio.sleep(random.uniform(0.1, 0.3) * 60)
    except TimeoutError:
        print("⏳ Échec, l'élément n'a pas chargé à temps")


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

        # Timeout global pour toutes les actions (clic, saisie, wait_for, etc.)
        context.set_default_timeout(180000) # 7 minutes . click(), fill(), wait_for_selector(), locator.wait_for()
        context.set_default_navigation_timeout(180000) # Timeout global spécifique à la navigation (goto, reload, wait_for_url)

        # Charger les cookies AVANT d'ouvrir la page
        cookies = load_cookies()
        await context.add_cookies(cookies)

        page = await context.new_page()

        # appliquer stealth
        await apply_stealth(page)

        # await page.goto("https://www.facebook.com/MTNCONGO", timeout=0)
        await page.goto("https://www.facebook.com/mariuscaslameuse")
        # await page.goto("https://www.facebook.com/profile.php?id=100070685221881", timeout=0)

        await jaime(page)
        await commenter(page)

        # comments = await page.query_selector_all('div[role="textbox"][contenteditable="true"][aria-label*="Commenter en tant que"]')
        # print("1 Nombre de zones trouvées:", len(comments))

        # if len(comments) > 0:
        #    await comments[0].fill("🔥 Commentaire avec .length !")

        # Récupérer et sauvegarder la session complète (cookies + localStorage)
        # context.storage_state(path=SESSION_FILE)
        # print(f"✅ Session Playwright sauvegardée : {SESSION_FILE}")

        # Remplace time.sleep par asyncio.sleep (non bloquant)
        await asyncio.sleep(10000)

        # Exemple : récupérer le nom du compte (si tu veux l’afficher)
        # try:
        #    account_name = await page.locator("h1").inner_text()
        #    print("Nom du compte :", account_name)
        # except Exception as e:
        #    print("Impossible de récupérer le nom du compte :", e)

        # await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
