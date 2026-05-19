// serveur.js
const express = require('express');
const fs = require('fs');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(express.json());
app.use(cors());

// Servir l'interface graphique de RapidCode
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "codegen3.html"));
});

// Objet de gestion du NoCode - Adapté à la réception des briques linéaires
const BriquesNoCode = {
    /**
     * Compile un tableau de chaînes (lignes de code pré-indentées) en un bloc de script unifié.
     * Ajoute obligatoirement et de manière sécurisée la ligne de lancement événementielle à la fin.
     */
    compilerWorkflowLineaire: (etapes) => {
        if (!etapes || !Array.isArray(etapes)) {
            return "# Erreur : Aucun workflow valide reçu par le compilateur.";
        }
        
        // Jointure simple de chaque élément du tableau avec un saut de ligne
        let codeFinal = etapes.join("\n");

        // SÉCURITÉ : Validation de la présence de la brique de lancement de boucle événementielle
        if (!codeFinal.includes("asyncio.run(main())")) {
            codeFinal += "\n\nasyncio.run(main())\n";
        }

        return codeFinal;
    }
};

// Route principale pour la génération du workflow universel linéaire
app.post('/generer-workflow-universel', (req, res) => {
    try {
        const { fichier, etapes } = req.body;

        // Validation stricte des données d'entrée
        if (!fichier || !etapes) {
            return res.status(400).json({ 
                statut: "erreur", 
                message: "Le nom du fichier de destination et la liste des étapes sont obligatoires." 
            });
        }

        // Normalisation du chemin pour accepter "../" proprement
        const cheminNormalise = path.normalize(fichier);
        
        // Validation de sécurité : s'assurer que l'extension reste bien .py
        if (!cheminNormalise.endsWith('.py')) {
            return res.status(400).json({ 
                statut: "erreur", 
                message: "L'extension du fichier généré doit impérativement être '.py'." 
            });
        }

        // Résolution finale du chemin physique absolu (par rapport au dossier courant du serveur)
        const cheminDestination = path.resolve(__dirname, cheminNormalise);

        // Assemblage propre via notre module de compilation linéaire (avec ajout forcé de asyncio.run)
        const scriptPythonComplet = BriquesNoCode.compilerWorkflowLineaire(etapes);

        // Écriture physique du script Python autonome (en UTF-8)
        fs.writeFileSync(cheminDestination, scriptPythonComplet, 'utf-8');

        console.log(`[RapidCode] Script généré avec succès dans : ${cheminDestination}`);
        
        return res.status(200).json({ 
            statut: "succes", 
            message: `Le script a été produit sans erreur dans le dossier parent.`,
            chemin: cheminDestination 
        });

    } catch (error) {
        console.error("[RapidCode] Erreur interne du serveur lors de la compilation :", error);
        return res.status(500).json({ 
            statut: "erreur", 
            message: "Erreur interne critique lors de l'écriture du script Python.",
            ctx: error.message 
        });
    }
});

// Démarrage épuré du serveur sur le port 3000
const PORT = 3000;
app.listen(PORT, () => {
    console.log("Serveur disponible sur : http://localhost:" + PORT);
});
