// serveur.js
const express = require('express');
const fs = require('fs');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(express.json());
app.use(cors());

app.get("/", (req, res) => {
    res.sendFile(__dirname + "/codegen2.html");
});

const BriquesNoCode = {
    // PARTIE 1 : Les 7 Cas d'Initialisation et de Filtrage de fichiers complexes
    no_code_init_fichiers: (params, indentation) => {
        const ind = " ".repeat(indentation);
        const ind2 = " ".repeat(indentation + 4);
        let code = "";
        
        switch (params.cas) {
            case "collecter_liens_fb":
                code += `${ind}fichier_des_comptes = "${params.f_comptes || 'mes_comptes_fb2.json'}"\n`;
                code += `${ind}comptes = await charger_comptes(fichier_des_comptes)\n`;
                code += `${ind}comptes = [c for c in comptes if c.get("message") == 1]\n`;
                code += `${ind}comptes = [c for c in comptes if not str(c.get("fichier", "")).strip().startswith("-")]`;
                break;
                
            case "envoyer_email":
                code += `${ind}fichier1 = "${params.f1 || 'emails_collecter.json'}"\n`;
                code += `${ind}fichier2 = "${params.f2 || 'emails_collecter2.json'}"\n`;
                code += `${ind}emails = await verifier_nouveau_element(fichier1, fichier2, "email")\n`;
                code += `${ind}emails = [e for e in emails if await verifier_date_recontacte(e)]\n\n`;
                code += `${ind}fichier3 = "${params.f3 || 'mes_emails.json'}"\n`;
                code += `${ind}fichier4 = "${params.f4 || 'mes_emails2.json'}"\n`;
                code += `${ind}compte_emails = await verifier_nouveau_element(fichier3, fichier4, "email")\n`;
                code += `${ind}compte_emails = [c for c in compte_emails if await verifier_date_recontacte(c)]\n\n`;
                code += `${ind}fichier_email_debut = "${params.f_debut || 'email_debut.json'}"\n`;
                code += `${ind}email_debut = (await charger_fichier_d(fichier_email_debut)).get("email")\n\n`;
                code += `${ind}index = next((i for i, mail in enumerate(emails) if mail["email"] == email_debut), 0)`;
                break;
                
            case "like_bs":
                code += `${ind}comptes = await charger_fichier("${params.f_comptes || 'comptes-bs.json'}")\n`;
                code += `${ind}comptes = [c for c in comptes if not c["fichier"].startswith("-")]\n\n`;
                code += `${ind}pages_list = await charger_fichier("${params.f_pages || 'page_active_bs.json'}")\n`;
                code += `${ind}pages_list = [p for p in pages_list if "url" in p]\n`;
                code += `${ind}from itertools import cycle\n`;
                code += `${ind}cycle_pages = cycle(pages_list)\n\n`;
                code += `${ind}fichier_derniere_page = "${params.f_derniere || 'derniere_page_bs.json'}"\n`;
                code += `${ind}data = await charger_fichier_d(fichier_derniere_page)\n`;
                code += `${ind}derniere_page = data.get("name")`;
                break;
                
            case "envoyer_message_fb":
                code += `${ind}fichier1 = "${params.f1 || 'page_messages_collecter.json'}"\n`;
                code += `${ind}fichier2 = "${params.f2 || 'page_messages_collecter2.json'}"\n`;
                code += `${ind}pages_fb = await verifier_nouveau_element(fichier1, fichier2, "message")\n`;
                code += `${ind}pages_fb = [p for p in pages_fb if await verifier_date_recontacte(p)]\n\n`;
                code += `${ind}fichier3 = "${params.f3 || 'mes_comptes_fb.json'}"\n`;
                code += `${ind}fichier4 = "${params.f4 || 'mes_comptes_fb2.json'}"\n`;
                code += `${ind}comptes_fb = await verifier_nouveau_element(fichier3, fichier4, "message")\n`;
                code += `${ind}comptes_fb = [c for c in comptes_fb if await verifier_date_recontacte(c) and c.get("message") == 1]\n\n`;
                code += `${ind}fichier_page_message_debut = "${params.f_debut || 'fichier_page_message_debut.json'}"\n`;
                code += `${ind}page_message_debut = (await charger_fichier_d(fichier_page_message_debut)).get("message")\n\n`;
                code += `${ind}index = next((i for i, page in enumerate(pages_fb) if page["message"] == page_message_debut), 0)\n`;
                code += `${ind}page_suivant = None\n`;
                code += `${ind}pages_deja_contacter = set()\n`;
                code += `${ind}tour = 0\n\n`;
                code += `${ind}if len(comptes_fb) == 0:\n`;
                code += `${" ".repeat(indentation + 4)}print("Tout les comptes ont été utilisés")`;
                break;
                
            case "like_fb":
                code += `${ind}pages_list = await charger_fichier("${params.f_pages || 'page_active.json'}")\n`;
                code += `${ind}comptes = await charger_fichier("${params.f_comptes || 'mes_comptes_fb.json'}")\n\n`;
                code += `${ind}fichier_derniere_page = "${params.f_derniere || 'derniere_page_fb.json'}"\n`;
                code += `${ind}data = await charger_fichier_d(fichier_derniere_page)\n`;
                code += `${ind}derniere_page = data.get("name")\n`;
                code += `${ind}debut = False\n\n`;
                code += `${ind}# FILTRAGE AVANT\n`;
                code += `${ind}comptes = [c for c in comptes if not c["fichier"].startswith("-")]\n`;
                code += `${ind}pages_list = [p for p in pages_list if "url" in p]\n`;
                code += `${ind}from itertools import cycle\n`;
                code += `${ind}cycle_pages = cycle(pages_list)\n\n`;
                code += `${ind}# BOUCLE POUR TROUVER LA PAGE DE REPRISE\n`;
                code += `${ind}if derniere_page:\n`;
                code += `${ind2}while True:\n`;
                code += `${ind2}    page = next(cycle_pages)\n`;
                code += `${ind2}    name = page.get("name")\n`;
                code += `${ind2}    if derniere_page == name:\n`;
                code += `${ind2}        debut = True\n`;
                code += `${ind2}        break\n`;
                code += `${ind2}    if not debut:\n`;
                code += `${ind2}        continue`;
                break;
                
            case "deja_liker_fb":
                code += `${ind}pages_list = await charger_fichier("${params.f_pages || 'pages-tout-pays.json'}")\n`;
                code += `${ind}comptes = await charger_fichier("${params.f_comptes || 'comptes-fb.json'}")\n`;
                code += `${ind}derniere_page = (await charger_fichier("${params.f_derniere || 'derniere_page_pdj.json'}")).get("name")\n`;
                code += `${ind}debut = False\n\n`;
                code += `${ind}# FILTRAGE AVANT\n`;
                code += `${ind}comptes = [c for c in comptes if not c["fichier"].startswith("-")]\n`;
                code += `${ind}pages_list = [p for p in pages_list if "url" in p]`;
                break;
                
            case "visiter_page_fb":
                code += `${ind}comptes = json.load(open("${params.f_comptes || 'comptes-fb.json'}", encoding="utf-8"))`;
                break;
                
            default:
                code += `${ind}pass`;
        }
        return code;
    },

    // PARTIE 2 : Les 7 structures de Boucles Réelles
    no_code_init_boucles: (params, indentation) => {
        const ind = " ".repeat(indentation);
        const ind2 = " ".repeat(indentation + 4);
        let code = "";

        switch (params.cas) {
            case "collecter_liens_fb":
                code += `${ind}count = 0\n`;
                code += `${ind}while count < 2:\n`;
                code += `${ind2}for compte in comptes:`;
                break;

            case "envoyer_email":
                code += `${ind}for compte_email in compte_emails:\n`;
                code += `${ind2}tour += 1`;
                break;

            case "like_bs":
                code += `${ind}debut = False\n`;
                code += `${ind}count = 0\n`;
                code += `${ind}while count < 3:\n`;
                code += `${ind2}for compte in comptes:`;
                break;

            case "envoyer_message_fb":
                code += `${ind}for compte_fb in comptes_fb:\n`;
                code += `${ind2}tour += 1`;
                break;

            case "like_fb":
                code += `${ind}count = 0\n`;
                code += `${ind}while count < 2:\n`;
                code += `${ind2}count += 1\n`;
                code += `${ind2}for compte in comptes:\n`;
                code += `${" ".repeat(indentation + 8)}page = next(cycle_pages)`;
                break;

            case "deja_liker_fb":
                code += `${ind}while True:\n`;
                code += `${ind2}for compte in comptes:`;
                break;

            case "visiter_page_fb":
                code += `${ind}for index, compte in enumerate(comptes):`;
                break;

            default:
                code += `${ind}# Aucune structure de boucle définie`;
        }
        return code;
    },

    // PARAMÈTRES DU NAVIGATEUR & FURTIVITÉ
    no_code_init_navigateur: (params, indentation) => {
        const ind = " ".repeat(indentation);
        let code = "";
        if (params.cas === "stealth_cookies") {
            code += `${ind}# Configuration de sécurité standard Playwright\n`;
            code += `${ind}context = await browser.new_context(viewport={"width": 1280, "height": 720})\n`;
            code += `${ind}await apply_stealth(context)\n`;
            code += `${ind}page = await context.new_page()`;
        } 
        else if (params.cas === "connexion_initiale") {
            code += `${ind}context = await browser.new_context()\n`;
            code += `${ind}page = await context.new_page()`;
        }
        return code;
    },

    creer_fonction: (params, indentation) => {
        return `\n${" ".repeat(indentation)}async def ${params.nom}(${params.args || ''}):`;
    },

    no_code_combinateur: (params, indentation) => {
        const ind = " ".repeat(indentation);
        const ind2 = " ".repeat(indentation + 4);
        let code = "";
        if (params.mode === "produit_cartesien") {
            code += `${ind}import itertools\n`;
            code += `${ind}for compte, page in itertools.product(${params.comptes}, ${params.pages}):`;
        } 
        else if (params.mode === "un_pour_un") {
            code += `${ind}for compte, page in zip(${params.comptes}, ${params.pages}):`;
        } 
        else if (params.mode === "aleatoire") {
            code += `${ind}import random\n`;
            code += `${ind}for page in ${params.pages}:\n`;
            code += `${ind2}compte = random.choice(${params.comptes})`;
        } 
        else if (params.mode === "round_robin") {
            code += `${ind}import itertools\n`;
            code += `${ind}if not hasattr(main, "_cycle_${params.comptes}"):\n`;
            code += `${ind2}main._cycle_${params.comptes} = itertools.cycle(${params.comptes})\n`;
            code += `${ind}for page in ${params.pages}:\n`;
            code += `${ind2}compte = next(main._cycle_${params.comptes})`;
        }
        return code;
    },

    no_code_scrape: (params, indentation) => {
        const ind = " ".repeat(indentation);
        const ind2 = " ".repeat(indentation + 4);
        let code = "";
        if (params.target === "query_selector") {
            code += `${ind}element_detecte = await page.query_selector("${params.css}")\n`;
            code += `${ind}${params.vname} = None\n`;
            code += `${ind}if element_detecte:\n`;
            if (params.dtype === "attribut") {
                code += `${ind2}${params.vname} = await element_detecte.get_attribute("${params.attr}")`;
            } else {
                code += `${ind2}${params.vname} = await element_detecte.text_content()`;
            }
        } else if (params.target === "locator_first") {
            code += `${ind}try:\n`;
            code += `${ind2}${params.vname} = await page.locator("${params.css}").first.text_content()`;
            code += `\n${ind}except:\n${ind2}${params.vname} = None`;
        }
        return code;
    },

    no_code_clean: (params, indentation) => {
        const ind = " ".repeat(indentation);
        const ind2 = " ".repeat(indentation + 4);
        let code = `${ind}if ${params.vname}:\n`;
        if (params.replace) {
            code += `${ind2}${params.vname} = ${params.vname}.replace("${params.replace}", "")\n`;
        }
        if (params.strip) {
            code += `${ind2}${params.vname} = ${params.vname}.strip()`;
        }
        return code;
    },

    no_code_filter: (params, indentation) => {
        const ind = " ".repeat(indentation);
        let expr = "";
        if (params.rule === "endswith") expr = `${params.vname}.endswith("${params.val}")`;
        if (params.rule === "startswith") expr = `${params.vname}.startswith("${params.val}")`;
        if (params.rule === "contains") expr = `"${params.val}" in ${params.vname}`;
        if (params.rule === "exists") expr = `${params.vname}`;
        return `${ind}if ${params.vname} and ${expr}:`;
    },

    no_code_database: (params, indentation) => {
        const ind = " ".repeat(indentation);
        let netData = (params.data || "{}").replace(/'/g, '"');
        if (params.action === "mettre_a_jour") {
            return `${ind}await mettre_a_jour("${params.file}", ${netData}, "${params.key}", ${params.match})`;
        } else {
            return `${ind}await ajouter_dans_fichier("${params.file}", ${netData}, "${params.key}", ${params.match})`;
        }
    },

    fin_bloc: () => ""
};

function compilerEtapes(etapesList, baseIndentation) {
    let codeResultat = "";
    let niveauIndentation = baseIndentation;

    etapesList.forEach((etape) => {
        if (etape.type === "fin_bloc") {
            niveauIndentation -= 4;
            if (niveauIndentation < 0) niveauIndentation = 0;
            return;
        }

        if (BriquesNoCode[etape.type]) {
            codeResultat += BriquesNoCode[etape.type](etape.params, niveauIndentation) + "\n";

            // Augmenter l'indentation si c'est un bloc ouvrant de contrôle
            if (["creer_fonction", "no_code_filter", "no_code_scrape", "no_code_clean", "no_code_combinateur", "no_code_init_boucles"].includes(etape.type)) {
                niveauIndentation += 4;
                // Cas spécifique de la boucle imbriquée double (cas 1, 3, 5, 6)
                if (etape.type === "no_code_init_boucles" && ["collecter_liens_fb", "like_bs", "like_fb", "deja_liker_fb"].includes(etape.params.cas)) {
                    niveauIndentation += 4;
                }
            }
        }
    });
    return codeResultat;
}

app.post('/generer-workflow-universel', (req, res) => {
    const { fichier_destination, etapes } = req.body;
    if (!fichier_destination || !etapes) return res.status(400).json({ message: "Données manquantes" });

    const cheminAbsoluCible = path.resolve(__dirname, fichier_destination);
    let etapesFonctionsGlobales = [];
    let etapesMain = [];
    let dansUneFonctionGlobale = false;
    let profondsIndentsDeFonction = 0;

    etapes.forEach((etape) => {
        if (etape.type === "creer_fonction") dansUneFonctionGlobale = true;

        if (dansUneFonctionGlobale) {
            etapesFonctionsGlobales.push(etape);
            if (["creer_fonction", "no_code_filter", "no_code_scrape", "no_code_clean", "no_code_combinateur", "no_code_init_boucles"].includes(etape.type)) {
                profondsIndentsDeFonction += 4;
            }
            if (etape.type === "fin_bloc") profondsIndentsDeFonction -= 4;
            if (profondsIndentsDeFonction <= 0) dansUneFonctionGlobale = false;
        } else {
            etapesMain.push(etape);
        }
    });

    let codeFinal = `# -*- coding: utf-8 -*-\nimport json, asyncio, time, msvcrt\nfrom playwright.async_api import async_playwright\nfrom datetime import datetime, timedelta\nfrom outils_playwright import *\n\nformat_date = "%d-%m-%Y"\n`;

    if (etapesFonctionsGlobales.length > 0) codeFinal += compilerEtapes(etapesFonctionsGlobales, 0);

    codeFinal += `\nasync def main():\n    async with async_playwright() as p:\n        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars", "--disable-web-security"])\n`;

    codeFinal += compilerEtapes(etapesMain, 8);
    codeFinal += "\n        await browser.close()\n\nasyncio.run(main())\n";

    fs.writeFile(cheminAbsoluCible, codeFinal, 'utf8', (err) => {
        if (err) return res.status(500).json({ message: "Erreur écriture" });
        res.json({ message: `Fichier enregistré avec succès : ${cheminAbsoluCible}` });
    });
});

app.listen(3000, () => console.log('Serveur démarré sur http://localhost:3000'));
