const express = require('express');
const fs = require('fs');
const app = express();
app.use(express.json());

app.post('/ajouter-import', (req, res) => {
	const { line, fonction } = req.body;
    const filePath = '../envoyer-message.py'; // ton fichier à modifier

    // Lire le contenu du fichier
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) { return res.status(500).json({ message: 'Erreur lecture fichier' }); }
		
		
		const importRegex = /^from outils_playwright import \(([^)]*)\)/m;
        const match = data.match(importRegex);
		const importLine = `from outils_playwright import (${fonction})`;
		
        if (match) {
            // La ligne d'import existe, on récupère la liste d'import
            const imports = match[1].split(',').map(s => s.trim());

            if (!imports.includes(fonction)) {
                // Ajoute 'clic_text' si pas dedans
                imports.push(fonction);
                const newImportLine = `from outils_playwright import (${imports.join(', ')})`;
                data = data.replace(importRegex, newImportLine);
            }
        } else {
            data = `${importLine}\n` + data; // Ajouter la ligne d'import en haut . La ligne d'import n'existe pas, on l'ajoute en haut
        }
		
		
		// Traite la chaîne 'line' pour construire l'appel
        const selectors = line.split(',').map(s => s.trim()).filter(Boolean); // sépare par virgule		
        if (selectors.length === 0) { return res.status(400).json({ message: "Aucun selecteur fourni" }); } // sécurité - arrete , si aucun selecteur
		
        const formattedSelectors = selectors.map(s => `"${s}"`); // formatter le selecteur
		const appelContenu = `await ${fonction}(page, [${formattedSelectors.join(', ')}])`;
		
		
		const regex = /(await creer_compte_th\([^\n]*\))/;
		let finalContenu;

		if (regex.test(data)) { finalContenu = data.replace(regex, `$1\n            ${appelContenu}`); } // s'il a trouvé la regex, il ajoute le code juste après
		else { finalContenu = data + `\n\n${appelContenu}\n`; } // Sinon, il ajoute le code en bas du fichier


        // Écrire le nouveau contenu dans le fichier
        fs.writeFile(filePath, finalContenu, 'utf8', (err) => {
            if (err) { return res.status(500).json({ message: 'Erreur écriture fichier' }); }
            res.json({ message: 'Ligne ajoutée en haut du fichier' });
        });
    });
});


app.get("/", (req, res) => {
    res.sendFile(__dirname + "/codegen.html");
});



app.listen(3000, () => {
    console.log('Serveur lancé sur http://localhost:3000');
});