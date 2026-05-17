const express = require('express');
const fs = require('fs');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Moteur de rendu des briques No-Code Universelles
const BriquesNoCode = {
    boucle_compteur: (params, indentation, outils) => {
        const ind = " ".repeat(indentation);
        return `${ind}${params.variable_compteur} = 0\n${ind}while ${params.variable_compteur} < ${params.limite_cycles}:`;
    },

    boucle_rotation: (params, indentation, outils) => {
        const ind = " ".repeat(indentation);
        return `${ind}for ${params.variable_acteur} in ${params.liste_acteurs}:`;
    },

    ouvrir_session_isolee: (params, indentation, outils) => {
        const ind = " ".repeat(indentation);
        let code = "";
        code += `${ind}context = await browser.new_context()  # Nouveau contexte pour chaque ${params.variable_acteur}\n`;
        code += `${ind}cookies = charger_cookies("${params.chemin_stockage}")  # Charger les cookies AVANT d'ouvrir la page\n`;
        code += `${ind}await context.add_cookies(cookies)\n`;
        code += `${ind}page = await context.new_page()`;
        
        if (params.activer_stealth) {
            code += `\n${ind}await apply_stealth(page)`;
        }
        return code;
    },

    // La brique de synchronisation dynamique modifiée pour utiliser des variables locales
    synchroniseur: (params, indentation, outils) => {
        const ind = " ".repeat(indentation);
        
        // Incrémentation de l'index des variables pour éviter l'écrasement (ex: fichier1, fichier2 puis fichier3, fichier4)
        const v1 = `fichier${outils.compteurFichiers}`;
        outils.compteurFichiers++;
        const v2 = `fichier${outils.compteurFichiers}`;
        outils.compteurFichiers++;

        let code = "";
        code += `${ind}${v1} = "${params.fichier1}"\n`;
        code += `${ind}${v2} = "${params.fichier2}"\n`;
        code += `${ind}${params.variable_sortie} = await verifier_nouveau_element(${v1}, ${v2}, "${params.cle_db}")`;
        
        if (params.filtrer_date) {
            // Extrait la première lettre pour la list comprehension python (ex: pages_fb -> p)
            const lettreId = params.variable_sortie.charAt(0); 
            code += `\n${ind}${params.variable_sortie} = [${lettreId} for ${lettreId} in ${params.variable_sortie} if await verifier_date_recontacte(${lettreId})]`;
        }
		return code + "\n";
    },

    action_simple: (params, indentation, outils) => {
        const ind = " ".repeat(indentation);
        return `${ind}await ${params.fonction}(${params.argument})`;
    }
};

// Endpoint principal universel
app.post('/generer-workflow-universel', (req, res) => {
    const { fichier_destination, etapes } = req.body;

    if (!fichier_destination || !etapes) {
        return res.status(400).json({ message: "Données manquantes" });
    }

    let codeFinal = `# -*- coding: utf-8 -*-\n# Code généré automatiquement via Codegen Studio Universel\n`;
    codeFinal += `import asyncio\n`;
    codeFinal += `from playwright.async_api import async_playwright\n`;
    codeFinal += `from outils_playwright import apply_stealth, verifier_nouveau_element\n\n`;
    
    codeFinal += `async def main():\n`;
    codeFinal += `    async with async_playwright() as p:\n`;
    codeFinal += `        browser = await p.chromium.launch(\n`;
    codeFinal += `            headless=False,\n`;
    codeFinal += `            args=[\n`;
    codeFinal += `                "--disable-blink-features=AutomationControlled",\n`;
    codeFinal += `                "--no-sandbox",\n`;
    codeFinal += `                "--disable-infobars",\n`;
    codeFinal += `                "--disable-web-security",\n`;
    codeFinal += `            ],\n`;
    codeFinal += `        )\n\n`;

    let niveauIndentation = 8;
    
    // Objet partagé contenant le compteur global d'index des fichiers pour la session courante
    let outilsSession = { compteurFichiers: 1 };

    etapes.forEach((etape) => {
        if (BriquesNoCode[etape.type]) {
            const ligneGeneree = BriquesNoCode[etape.type](etape.params, niveauIndentation, outilsSession);
            codeFinal += ligneGeneree + "\n";

            if (etape.type === "boucle_rotation" || etape.type === "boucle_compteur") {
                niveauIndentation += 4;
            }
        }
    });

    codeFinal += "\nif __name__ == '__main__':\n    asyncio.run(main())\n";

    fs.writeFile(fichier_destination, codeFinal, 'utf8', (err) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ message: "Erreur lors de l'écriture du fichier" });
        }
        res.json({ message: `Fichier ${fichier_destination} généré avec succès !` });
    });
});

app.get("/", (req, res) => {
    res.sendFile(__dirname + "/codegen2.html");
});


app.listen(3000, () => {
    console.log('Serveur Universel Codegen démarré sur http://localhost:3000');
});
