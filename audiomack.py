import json
import asyncio, random
from playwright.async_api import async_playwright
import traceback


async def apply_stealth(page):
    await page.add_init_script(
        """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    """
    )


def load_cookies(file_path="cookies-audiomack.json"):
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


async def safe_action(action, *args, retries=5, wait=60, **kwargs):
    """
    Exécute une action Playwright avec retry automatique si internet coupe.
    - action: fonction Playwright (ex: page.goto, page.click, page.fill)
    - retries: nombre d'essais
    - wait: temps d'attente (en secondes) entre deux essais
    """
    for attempt in range(1, retries + 1):
        try:
            # print("on est connecté à internet")
            return await action(*args, **kwargs)
        except Exception as e:
            print(
                f"Pas de connexion internet. {e} (on patiente et reessaie {attempt}/{retries})"
            )
            if attempt < retries:
                print(
                    f"⏳ Attendre {wait}s que internet revienne d'abord, avant de dire au script de réessayer, de continuer d'avancer"
                )
                await asyncio.sleep(wait)
            else:
                print("❌ Abandon après 5 min à attendre que internet revienne")
                raise


async def recuperer_lien(page):
    try:
        print("Récupérer le lien")
        print("on attend que la section Highlighted soit visible")
        await safe_action(page.wait_for_selector, "header:has-text('Highlighted')")
        # await page.wait_for_selector("header:has-text('Highlighted')")

        # Localiser le conteneur Highlighted
        highlighted = page.locator("header:has-text('Highlighted')").locator("..")

        # Prendre le premier lien de chanson dans ce bloc
        print("c'est visible, on récupère le lien")
        getlien = await safe_action(
            highlighted.locator("a[href*='/song/']").first.get_attribute, "href"
        )
        # getlien = await highlighted.locator("a[href*='/song/']").first.get_attribute("href")

        if not getlien:
            print("❌ Aucun lien trouvé dans Highlighted")
            return None

        print("on colle le lien")
        lien = "https://audiomack.com" + getlien

        print("Lien de la chanson récente :", lien)
        return lien
    except Exception as e:
        print("Erreur lors de la récupération du lien :", e)
        traceback.print_exc()
        return None


async def envoyer_commentaire(page):
    try:
        print("on attend que le champ de Commentaire soit visible")
        await safe_action(page.wait_for_selector, '[data-testid="field-input"]')
        # await page.wait_for_selector('[data-testid="field-input"]')

        print("c'est visible. ecrire le Commentaire")
        await safe_action(page.fill, '[data-testid="field-input"]', "tokoos ! 🔥")
        # await page.fill('[data-testid="field-input"]', "aigleee ! 🔥")
        # await page.fill('textarea[name="comment"]', "belle musique ! 🔥")

        print("on a écrit, on patiente quelques secondes")
        await asyncio.sleep(random.uniform(0.1, 0.3) * 60)

        print("on attend que le bouton pour envoyer le Commentaire soit visible")
        await safe_action(page.wait_for_selector, 'button[type="submit"]')
        # await page.wait_for_selector('button[type="submit"]')

        print("c'est visible, on envoie le Commentaire")
        await safe_action(page.click, 'button[type="submit"]')

        # await page.click('button[type="submit"]')
        print("✅ Commentaire envoyé !")

        print("on a envoyé, on patiente quelques secondes")
        await asyncio.sleep(random.uniform(0.3, 1) * 60)
    except Exception as e:
        print("Erreur lors du commentaire:", e)
        traceback.print_exc()


async def main():
    try:
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
            context.set_default_timeout(
                180000
            )  # 3 minutes . click(), fill(), wait_for_selector(), locator.wait_for()
            context.set_default_navigation_timeout(
                180000
            )  # Timeout global spécifique à la navigation (goto, reload, wait_for_url)

            # Charger les cookies AVANT d'ouvrir la page
            cookies = load_cookies()
            await safe_action(context.add_cookies, cookies)
            # await context.add_cookies(cookies)

            page = await safe_action(context.new_page)
            # page = await context.new_page()

            # appliquer stealth
            await apply_stealth(page)

            try:
                print("on va sur la page")
                await safe_action(page.goto, "https://audiomack.com/fally-ipupa")
                await safe_action(page.wait_for_load_state, "domcontentloaded")
                # await safe_action(page.goto, "https://audiomack.com/fally-ipupa", timeout=0)
                # await page.wait_for_load_state("domcontentloaded")
                # await page.goto("https://audiomack.com/fally-ipupa", timeout=0)
            except Exception as e:
                print("Erreur lors du chargement de la page :")
                print(e)
                traceback.print_exc()
                await browser.close()
                return

            highlighted_link = await recuperer_lien(page)
            if highlighted_link:
                # print("Lien de la chanson :", highlighted_link)

                print("on va sur la page de la chanson", highlighted_link)
                await safe_action(page.goto, highlighted_link)
                await safe_action(page.wait_for_load_state, "domcontentloaded")
                # await safe_action(page.goto, highlighted_link, timeout=0)
                # await page.wait_for_load_state("domcontentloaded")
                # await page.goto(highlighted_link, timeout=0)
            else:
                print("Aucun lien trouvé après le header HIGHLIGHTED")

            await envoyer_commentaire(page)
            await asyncio.sleep(10000)
            # await browser.close()
    except Exception as e:
        print("Erreur générale :")
        print(e)
        traceback.print_exc()
    finally:
        if "browser" in locals():
            await safe_action(browser.close)
            print("Fermeture du navigateur")
            # await browser.close()


asyncio.run(main())
