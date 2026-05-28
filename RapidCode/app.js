let indexFonctionCible = null; // null = comportement normal
let fonctionOuverte = null; // stocke l'index de la fonction dont la liste est déroulée
let resultat = document.getElementById("resultat");
let interfacee = document.getElementById("bloc");

resultat.addEventListener('input', afficherFonctions);


const textes = [
  { texte: "instruction1 = await browser.new_context()" },
  { texte: "instruction2 = charger_cookies(fichier_cookie)" },
  { texte: "await instruction1.add_cookies(instruction2)" }
];

const html = textes.map(data => {
  return `
    <div class="bloc">
      <p>${data.texte}</p>
    </div>
  `;
}).join("");

interfacee.innerHTML = html;


const blocs = interfacee.querySelectorAll(".bloc");
blocs.forEach(function(bloc) {
  bloc.onclick = function() {
	if (fonctionOuverte === null) return; // aucune fonction ouverte → on fait rien

	let texteInterface = bloc.innerText; // texteActuel
	let textarea = resultat.value;
    //console.log("aa", texteInterface);
	
    const phraseCible = "async def";

	const regex = new RegExp(
	  phraseCible
		.split(" ")
		.map(mot => mot.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
		.join("\\s+"),
	  "i"
	); 
	
	if (regex.test(textarea)) { // Vérifie si phrase cible est dans le textarea
		//console.log("texteInterface trouvé");
		  const lignes = textarea.split('\n');
		  
		  const nouvLignes = lignes.map(ligne => {
			if (regex.test(ligne)) {
			  // ajoute le texte du bloc à la ligne suivante, indenté
			  return ligne + '\n    ' + texteInterface;
			}
			return ligne;
		  });
		  resultat.value = nouvLignes.join('\n');
		  afficherFonctions();
    } else {
	  //console.log("pas de texteInterface");
	  resultat.value += '\n' + texteInterface; // Sinon, remplace tout le contenu par le texteInterface
	  afficherFonctions();
    }
}		
});		



function afficherFonctions() {
  const textarea = resultat.value;
  const lignes = textarea.split('\n');
  const liste = document.getElementById("liste_fonctions_utilisateur");
  
  
  // 1. Sauvegarder les index ouverts AVANT de reconstruire
  const ouvertAvant = new Set();
  liste.querySelectorAll('div[id^="instructions-"]').forEach(div => {
    if (div.style.display === 'flex') {
      const index = div.id.replace('instructions-', '');
      ouvertAvant.add(index);
    }
  });
  
  // afficher les fonctions avec leurs lignes internes
  const fonctions = [];
  let fnCourante = null;

  lignes.forEach((ligne, indexLigne) => {
    if (/(?:async\s+)?def\s+/i.test(ligne)) { // cherche toutes les lignes qui contiennent "async def"
		
      fnCourante = { nom: ligne.trim(), instructions: [] }; // nouvelle fonction trouvée,  .trim() nettoie les espaces
      fonctions.push(fnCourante);
    } else if (fnCourante && ligne.trim() !== '') {
      
      fnCourante.instructions.push({ texte: ligne.trim(), indexLigne }); // ligne non-vide à l'intérieur d'une fonction
    }
  });

  if (fonctions.length === 0) { liste.innerHTML = ''; return; } // effacer la liste avant de return . si on a pas encore de fonctions dans le textarea, on evite que la suite de ce code ne s'execute.


  // --- afficher ---
  liste.innerHTML = fonctions.map((fn, i) => `
    <div style="margin-bottom:12px">

      <div class="bloc scroller-jusqua-fonction" style="display:flex; align-items:center; justify-content:space-between;">
        <span>${fn.nom}</span>
		
		<div style="display:flex; gap:6px;">
			<span data-index-fn="${i}" class="icon-inserer-fn" title="Insérer une fonction ici" style="cursor:pointer;">➕</span>
			<span data-index="${i}" id="toggle-liste-${i}" title="Ajouter une instruction" style="cursor:pointer;">📋</span>
			<span data-index="${i}" id="toggle-${i}" title="Dérouler/Enrouler" style="cursor:pointer;">▶</span> <!-- flèche dérouler/enrouler . id="toggle-0" pour i=0, "toggle-1" pour i=1... data-index stocke le numéro pour retrouver le bon div  -->
			<span data-fn="${fn.nom.replace(/"/g, '&quot;')}" class="icon-descendre" title="Aller à cette fonction">⤵</span> <!-- flèche scroller . data-fn stocke le nom de la fonction . utilisé par allerAFonction() pour scroller  -->
		</div>
      </div>

      <div id="instructions-${i}" style="padding-left:12px; margin-top:4px; display:none; flex-direction:column; gap:3px;"> <!-- instructions cachées par défaut -->
        ${fn.instructions.map(inst => `
		  <div style="display:flex; align-items:center; justify-content:space-between; font-size:12px; color:#555; padding:3px 8px; background:#f5f5f5; border-radius:5px;">
			<span>${inst.texte}</span>
			<span data-index-ligne="${inst.indexLigne}" class="icon-suppr" title="Supprimer cette ligne" style="cursor:pointer; color:#aaa; font-size:11px; padding:0 4px;">✕</span>
		  </div>
		`).join('')}
      </div>
	  
	    <div id="liste-blocs-${i}" style="display:none; flex-direction:column; gap:4px; margin-top:4px;">
		  ${textes.map(t => `
			<div class="bloc-instruction" data-index-fn="${i}" data-texte="${t.texte}" style="cursor:pointer; padding:4px 8px; background:#eef; border-radius:5px; font-size:12px;">
			  ${t.texte}
			</div>
		  `).join('')}
		</div>

    </div>
  `).join(''); // stocke dans data-attribute à la place .  data-fn , apparemment cest une element html qui permet de scroller jusqua la fonction - peut etre cest ca 

	
  // 2. Restaurer les listes qui étaient ouvertes
  ouvertAvant.forEach(index => {
    const div = document.getElementById('instructions-' + index);
    const toggle = document.getElementById('toggle-' + index);
    if (div) div.style.display = 'flex';
    if (toggle) toggle.textContent = '▼';
  });

    // onclick flèche toggle
	liste.querySelectorAll('span[id^="toggle-"]').forEach(toggle => {
	  toggle.onclick = () => {
		const index = toggle.dataset.index; //lit data-index → ex: "0"
		const div = document.getElementById('instructions-' + index); // trouve le bon div → "instructions-0"
		const ouvert = div.style.display === 'flex'; // est-ce que c'est déjà ouvert ?

		div.style.display = ouvert ? 'none' : 'flex'; // si ouvert → ferme (none) | si fermé → ouvre (flex)
		toggle.textContent = ouvert ? '▶' : '▼'; // ▶ fermé, ▼ ouvert .  change l'icône en conséquence
	  };
	});

    liste.querySelectorAll('span[data-fn]').forEach(fleche => { // onclick flèche scroll . lit data-fn → ex: "async def cool():"
      fleche.onclick = () => allerAFonction(fleche.dataset.fn);
    });
  
    
	liste.querySelectorAll('span.icon-suppr').forEach(btn => {
	  btn.onclick = (e) => {
		e.stopPropagation();
		const indexLigne = parseInt(btn.dataset.indexLigne); // bon attribut
		const lignes = resultat.value.split('\n');
		lignes.splice(indexLigne, 1); // supprime exactement cette ligne
		resultat.value = lignes.join('\n');
		afficherFonctions();
	  };
	});
	
	
	liste.querySelectorAll('span.icon-inserer-fn').forEach(btn => {
	  btn.onclick = () => {
		indexFonctionCible = parseInt(btn.dataset.indexFn); // stocke quelle fonction on vise
		ajouterFonctionDansEditor(); // ouvre la popup normalement
	  };
	});
	
	
	
	liste.querySelectorAll('span[id^="toggle-liste-"]').forEach(toggle => { // toggle — ouvre/ferme la liste des blocs
	  toggle.onclick = () => {
		const index = toggle.dataset.index;
		const div = document.getElementById('liste-blocs-' + index);
		const ouvert = div.style.display === 'flex';
		div.style.display = ouvert ? 'none' : 'flex';
		fonctionOuverte = ouvert ? null : parseInt(index);
	  };
	});


	
	liste.querySelectorAll('.bloc-instruction').forEach(bloc => { // clic sur un bloc dans la liste
	  bloc.onclick = () => {
		const texteInterface = bloc.dataset.texte;
		const indexFn = parseInt(bloc.dataset.indexFn);
		const lignes = resultat.value.split('\n');		
		let count = 0; // trouver la dernière ligne de cette fonction
		let debutFn = -1;
		let finFn = -1;

		const nouvLignes = lignes.map(ligne => {
		  if (/(?:async\s+)?def\s+/i.test(ligne)) {
			if (count === indexFn) {
			  count++;
			  return ligne + '\n    ' + texteInterface; // ajoute dans cette fonction uniquement
			}
			count++;
		  }
		  return ligne;
		});

		resultat.value = nouvLignes.join('\n');
		afficherFonctions();
	  };
	});
	
	
	liste.querySelectorAll('.bloc-instruction').forEach(bloc => {
	  bloc.onclick = () => {
		const texteInterface = bloc.dataset.texte;
		const indexFn = parseInt(bloc.dataset.indexFn);
		const lignes = resultat.value.split('\n');

		// trouver la dernière ligne de cette fonction
		let count = 0;
		let debutFn = -1;
		let finFn = -1;

		lignes.forEach((ligne, i) => {
		  if (/(?:async\s+)?def\s+/i.test(ligne)) {
			if (count === indexFn) debutFn = i; // début de la fonction ciblée
			else if (count > indexFn && finFn === -1) finFn = i - 1; // début de la suivante = fin de la ciblée
			count++;
		  }
		});

		if (finFn === -1) finFn = lignes.length - 1; // pas de fonction suivante → fin du textarea

		// reculer pour ignorer les lignes vides à la fin
		while (finFn > debutFn && lignes[finFn].trim() === '') finFn--;

		lignes.splice(finFn + 1, 0, '    ' + texteInterface); // insère après la dernière instruction
		resultat.value = lignes.join('\n');
		afficherFonctions();
	  };
	});
	
	
}



function ajouterFonctionDansEditor() {
	document.getElementById("popupFonction").style.display = "block";
	const inputNom = document.getElementById("popup_func_name");
	
	inputNom.value = "";
	document.getElementById("popup_func_params").value = "";
	document.getElementById("zone_params_popup").style.display = "none";
	inputNom.focus();
}


function suivantFonctionPopup() {
  const zoneParams = document.getElementById("zone_params_popup");
  zoneParams.style.display = 'block'; // affiche le champ params
  document.getElementById("popup_func_params").focus();
}


function validerFonctionPopup() {
  const name = document.getElementById("popup_func_name").value.trim();
  const params = document.getElementById("popup_func_params").value.trim(); // vide si on a pas cliqué Suivant, c'est pas grave
  //if (!name) { document.getElementById("popup_func_name").style.border = "1px solid red"; return; }

	const nouvelleFonction = `async def ${name}(${params}):`;
	const lignes = resultat.value.split('\n');
	
	if (indexFonctionCible !== null) {
		// trouver la ligne exacte de la fonction ciblée
		let count = 0;
		const lignesCible = lignes.findIndex(l => {
		  if (/(?:async\s+)?def\s+/i.test(l)) {
			if (count === indexFonctionCible) return true;
			count++;
		  }
		  return false;
		});	
		
		lignes.splice(lignesCible, 0, nouvelleFonction, '', ''); // insère AVANT la fonction ciblée
		resultat.value = lignes.join('\n');
		indexFonctionCible = null; // reset
		
	} else {
		// comportement normal : au dessus de la 1ère fonction
		const premiereDef = lignes.findIndex(l => /(?:async\s+)?def\s+/i.test(l)); // trouve l'index de la 1ère fonction

		if (premiereDef === -1) {
		  resultat.value += '\n' + nouvelleFonction; // pas de fonction → ajoute à la fin
		} else {
		  lignes.splice(premiereDef, 0, nouvelleFonction, '', ''); // insère AVANT la 1ère fonction
		  resultat.value = lignes.join('\n');
		}
	}

  // reset la popup
  document.getElementById("popup_func_name").value = '';
  document.getElementById("popup_func_params").value = '';
  document.getElementById("zone_params_popup").style.display = 'none';

  afficherFonctions();
  document.getElementById("popupFonction").style.display = "none"; //fermer la popup
}



function allerAFonction(nomFn) {
  const lignes = resultat.value.split('\n');
  const index = lignes.findIndex(l => l.trim() === nomFn);
  if (index === -1) return;
  
  const positionChar = lignes.slice(0, index).join('\n').length; // calcule le nombre de caractères avant cette ligne
  
  resultat.focus(); // place le curseur sur cette ligne
  resultat.setSelectionRange(positionChar, positionChar);
  
  const ligneHauteur = resultat.scrollHeight / lignes.length; // scroll jusqu'à cette ligne
  resultat.scrollTop = ligneHauteur * index;
}




		function creerFonctionDepuisUI() {
			const name = document.getElementById("new_func_name").value.trim();
			const params = document.getElementById("new_func_params").value.trim();
			//if (!name) return alert("Nom obligatoire");

			const code = `
			async def ${name}(${params}):
				
			`;

			const nouvelleBrique = {
				id: "user_" + Date.now(),
				label: `async def ${name}(${params})`,
				code: code
			};

			briquesDisponibles.push(nouvelleBrique);
			genererBibliotheque();
			ajouterLigne(nouvelleBrique.id);
			
		}
		
		
		
		function afficherInstructionsDisponibles() {

			const container = document.getElementById("liste_instructions");
			container.innerHTML = "";

			instructionsDisponibles.forEach((instruction, index) => {

				container.innerHTML += `
					<div class="instruction-item"
						 onclick="ajouterInstructionDepuisListe(${index})">

						${instruction.id ? `<strong>${instruction.id}</strong><br>` : ""}
						<code>${instruction.code.trim()}</code>

					</div>
				`;
			});
		}
		

		
		let fonctionSelectionnee = null;
		function selectionnerFonction(index) {
			fonctionSelectionnee = index;
			afficherInstructionsDisponibles(); // affiche seulement quand on clique
		}
		
		
		function ajouterInstructionDepuisListe(indexInstruction) {


    const instruction = instructionsDisponibles[indexInstruction];

    let codeFonction = workflowActif[fonctionSelectionnee].code;
    const lignesFonction = codeFonction.split("\n");

    const lignesInstruction = instruction.code
        .trim()
        .split("\n")
        .filter(l => l.trim() !== "")
        .map(l => "    " + l);

    lignesFonction.splice(
        lignesFonction.length - 1,
        0,
        ...lignesInstruction
    );

    workflowActif[fonctionSelectionnee].code =
        lignesFonction.join("\n");

    afficherWorkflow();

    document.getElementById("bigEditor").value =
        workflowActif.map(w => w.code).join("\n\n");
}

		
		let fonctionsUtilisateur = [];
		
		function afficherFonctionsUtilisateur() {
			const container = document.getElementById("liste_fonctions_utilisateur");
			container.innerHTML = "";

			fonctionsUtilisateur.forEach((f, index) => {
				container.innerHTML += `
					<div onclick="selectionnerFonction(${index})">
						${f.nom}(${f.params})
					</div>
				`;
			});
		}
				
		
		
		function analyserFonctionsDepuisEditor() {
			console.log("analyse lancée");
			
			const code = document.getElementById("bigEditor").value;
			console.log("CODE =", code);
			const regex = /async\s+def\s+(\w+)\((.*?)\)/g;

			let match;
			const result = [];

			while ((match = regex.exec(code)) !== null) {
				console.log("CODE =", code);
				
				result.push({
					nom: match[1],
					params: match[2],
					code: match[0]
				});
			}
			
			console.log("RESULTAT FINAL =", result);
			fonctionsUtilisateur = result;
			afficherFonctionsUtilisateur();
		}
		
				
		
		function insererFonctionAvantPremiereFonction(code, nouvelleFonction) {
			const lignes = code.split("\n");

			const index = lignes.findIndex(l =>
				l.trim().startsWith("async def") ||
				l.trim().startsWith("def ")
			);

			if (index === -1) {
				lignes.unshift(nouvelleFonction);
			} else {
				lignes.splice(index, 0, nouvelleFonction);
			}

			return lignes.join("\n");
		}
		

		function cocherAutomatiquement1CompteToutesPages() {
			const actif = document.getElementById('v_mode_automation').checked;
			document.getElementById('v_inclure_debut_false').checked = actif; // debut = False
			document.getElementById('v_inclure_boucle_pages_fb').checked = actif; // boucle pages
			
			majDependancePause(); // afficher le bloc pause automatiquement
			document.getElementById('v_activer_pause').checked = actif; // pause    
			//document.getElementById('v_activer_mise_a_jour').checked = actif; // mettre_a_jour
			document.getElementById('v_activer_preparation_compte').checked = actif; // Context + NewPage
			document.getElementById('activer_visiter_page').checked = actif;
			document.getElementById('activer_ami').checked = actif;

			//if (actif) { afficherToast("Mode Automation activé !"); } 
			//else { afficherToast("Mode Automation désactivé !"); }
		}
		

        function majDependanceCheckbox() {
            const filtreComptesCoche = document.getElementById('v_filtre_date_comptes').checked;
            document.getElementById('bloc_sous_filtre_strict').style.display = filtreComptesCoche ? 'block' : 'none';
            if(!filtreComptesCoche) {
                document.getElementById('v_activer_filtre_actif').checked = false;
            }
        }

        // Gérer l'affichage de l'option pause uniquement si la boucle complète est activée
        function majDependancePause() {
            const boucleCochee = document.getElementById('v_inclure_boucle_pages_fb').checked;
            document.getElementById('bloc_config_pause').style.display = boucleCochee ? 'block' : 'none';
            if(!boucleCochee) {
                document.getElementById('v_activer_pause').checked = false;
            }
        }

        const briquesDisponibles = [
            { id: "main_def", label: "async def main():", code: "async def main():" },
            { id: "p_init", label: "async with async_playwright() as p:", code: "    async with async_playwright() as p:" },
            { id: "browser_launch", label: "browser = await p.chromium.launch(...)", code: "        browser = await p.chromium.launch(\n            headless=False,\n            args=[\n                \"--disable-blink-features=AutomationControlled\",\n                \"--no-sandbox\",\n                \"--disable-infobars\",\n                \"--disable-web-security\",\n            ],\n        )" },
            { id: "msg_f1_f2", label: "Déclaration fichier1 & fichier2", code: "        fichier1 = \"pages_collecter.json\"\n        fichier2 = \"pages_collecter2.json\"" },
            { id: "msg_pages_fb", label: "pages_fb = verifier_nouveau_element(...)", code: "        pages_fb = await verifier_nouveau_element(fichier1, fichier2, \"page\")" },
            { id: "msg_filter_pages", label: "Filtrage pages_fb par date recontacte", code: "        pages_fb = [p for p in pages_fb if await verifier_date_recontacte(p)]" },
            { id: "msg_f3_f4", label: "Déclaration fichier3 & fichier4", code: "        fichier3 = \"mes_comptes_fb.json\"\n        fichier4 = \"mes_comptes_fb2.json\"" },
            { id: "msg_comptes_fb", label: "comptes_fb = verifier_nouveau_element(...)", code: "        comptes_fb = await verifier_nouveau_element(fichier3, fichier4, \"message\")" },
            { id: "msg_filter_comptes", label: "Filtrage comptes_fb actifs & recontacte", code: "        comptes_fb = [c for c in comptes_fb if await verifier_date_recontacte(c) and c.get(\"page\") == 1]" },
            { id: "msg_f_derniere_page", label: "Déclaration fichier_derniere_page", code: "        fichier_derniere_page = \"fichier_page_debut.json\"" },
            { id: "msg_load_derniere", label: "derniere_page = charger_fichier_d(...)", code: "        derniere_page = (await charger_fichier_d(fichier_derniere_page)).get(\"page\")" },
            { id: "msg_index_next", label: "index = next((i for i, page...))", code: "        index = next((i for i, page in enumerate(pages_fb) if page[\"page\"] == derniere_page), 0)" },
            { id: "msg_init_vars", label: "Init page_suivant, pages_deja_contacter, tour", code: "        page_suivant = None\n        pages_deja_contacter = set()\n        tour = 0" },
            { id: "msg_check_comptes_empty", label: "if len(comptes_fb) == 0:", code: "        if len(comptes_fb) == 0:\n            print(\"Tout les comptes ont été utilisés\")" },
            { id: "msg_for_compte", label: "for compte_fb in comptes_fb:", code: "        for compte_fb in comptes_fb:" },
            { id: "msg_tour_print", label: "tour += 1; print(index)", code: "            tour += 1\n            print(\"index \", index)" },
            { id: "msg_check_index_bounds", label: "if index+1 > len(pages_fb): break", code: "            if index+1 > len(pages_fb):\n                print(\"aucune page a contacter, car tous ont deja été contacter\", index); break" },
            { id: "msg_extract_vars", label: "Extraction variables boucle compte", code: "            page = pages_fb[index]\n            url_page = page[\"page\"]\n            fichier_cookie = compte_fb.get(\"fichier\")\n            mon_compte = compte_fb.get(\"fichier\")" },
            { id: "msg_check_deja_contacter", label: "if url_page in pages_deja_contacter: continue", code: "            if url_page in pages_deja_contacter: continue" },
            { id: "msg_print_contact", label: "print('Contacté :', url_page)", code: "            print(\"Contacté :\", url_page)" }
        ];

        let workflowActif = [];
		let editIndex = null;

        function genererBibliotheque() {
            const container = document.getElementById('bibliotheque_briques');
            container.innerHTML = '';
            briquesDisponibles.forEach(brique => {
                const div = document.createElement('div');
                div.className = 'brique-dispo';
                div.innerHTML = `
                    <span>${brique.label}</span>
                    <span class="btn-add" onclick="ajouterLigne('${brique.id}')">+ Ajouter</span>
                `;
                container.appendChild(div);
            });
        }

        function ajouterLigne(id) {
            const brique = briquesDisponibles.find(b => b.id === id);
            if (brique) {
                workflowActif.push({ ...brique, uid: Date.now() + Math.random() });
                afficherWorkflow();
            }
        }
		
		
		function ajouterInstructionDansFonction(indexFonction) {
			const nouvelleLigne = prompt("Nouvelle instruction :");

			if (!nouvelleLigne) return;
			let code = workflowActif[indexFonction].code;
			const lignes = code.split("\n");

			// chercher la ligne "pass"
			const indexPass = lignes.findIndex(l => l.trim() === "pass");
			if (indexPass !== -1) { // remplacer pass				
				lignes.splice(indexPass, 1,
					`    ${nouvelleLigne}`
				);

			} else { // ajouter avant la dernière ligne
				lignes.splice(lignes.length - 1, 0,
					`    ${nouvelleLigne}`
				);
			}

			workflowActif[indexFonction].code = lignes.join("\n");
			afficherWorkflow();
		}


        function ajouterGrosBlocLie() {
            const db1 = document.getElementById('v_cle_db1').value;
            const db2 = document.getElementById('v_cle_db2').value;
            const f1 = document.getElementById('v_fichier1').value;
            const f2 = document.getElementById('v_fichier2').value;
            const f3 = document.getElementById('v_fichier3').value;
            const f4 = document.getElementById('v_fichier4').value;
            const f_derniere = document.getElementById('v_fichier_derniere_page').value;
            
            const filtreDatePagesCoche = document.getElementById('v_filtre_date_pages').checked;
            const filtreDateComptesCoche = document.getElementById('v_filtre_date_comptes').checked;
            const filtreStrictCoche = document.getElementById('v_activer_filtre_actif').checked;
            const inclureDebutFalse = document.getElementById('v_inclure_debut_false').checked;
            const inclureLogiquePage = document.getElementById('v_inclure_logique_page').checked;
            const inclureBouclePagesFb = document.getElementById('v_inclure_boucle_pages_fb').checked;
            const activerPauseCoche = document.getElementById('v_activer_pause').checked;
            const activerPauseAmiCocher = document.getElementById('activer_pause_ami').checked;
			const valeurPause = document.getElementById('v_duree_pause').value;
			const valeurPauseAmi = document.getElementById('duree_pause_ami').value;
			const activerMiseAJour = document.getElementById('v_activer_mise_a_jour').checked;
			const activerPreparationCompte = document.getElementById('v_activer_preparation_compte').checked;
			const activerVisiterPage = document.getElementById('activer_visiter_page').checked;
			const activerAmi = document.getElementById('activer_ami').checked;
			

            let ligneFiltrePages = filtreDatePagesCoche ? `\n        pages_fb = [p for p in pages_fb if await verifier_date_recontacte(p)]` : "";

            let ligneFiltreComptes = "";
            if (filtreDateComptesCoche) {
                let conditionStrict = filtreStrictCoche ? ` and c.get(cle_db1) == 1` : ``;
                ligneFiltreComptes = `\n        comptes_fb = [c for c in comptes_fb if await verifier_date_recontacte(c)${conditionStrict}]`;
            }

            let ligneDebutFalse = inclureDebutFalse ? `\n        debut = False` : "";

            let codeInterneBoucleIndex = "";
            if (inclureLogiquePage) {
                codeInterneBoucleIndex = `\n            if index+1 > len(pages_fb):
                print("aucune page a contacter, car tous ont deja été contacter", index); break
            
            page = pages_fb[index]
            url_page = page[cle_db1]
            fichier_cookie = compte_fb.get(cle_db2)
            mon_compte = compte_fb.get(cle_db2)
            
            if url_page in pages_deja_contacter: continue
            
            print("Contacté :", url_page)`;
            }

			let codeActionsOptionnelles = "";

			if (activerVisiterPage) {
				codeActionsOptionnelles += `
                await visiter_page(context, fichier2, url_page)`;
			}

			if (activerMiseAJour) {
				codeActionsOptionnelles += `\n                await mettre_a_jour(fichier2, {"ami": 1}, cle_db1, url_page)`;
			}

			if (activerPauseCoche) {
				codeActionsOptionnelles += `\n                print("Patiente ${valeurPause}s"); await asyncio.sleep(${valeurPause})`;
			}
			

            let codeBouclePagesComplete = "";
			
			let codePreparationCompte = "";
			
			if (activerPreparationCompte) {
			codePreparationCompte = `
            # Charger les cookies AVANT d'ouvrir la page
            fichier_cookie = compte_fb.get(cle_db2)
            
            context = await browser.new_context()
            cookies = charger_cookies(fichier_cookie)
            await context.add_cookies(cookies)
                
            page = await context.new_page()
            await appliquer_stealth(page)
            await page.goto("https://fb.com", timeout=0)\n`; }
			
            if (inclureBouclePagesFb) {
                codeBouclePagesComplete = `\n            for une_page in pages_fb:
                url_page = une_page.get('page')
                name = une_page.get('nom')
                fichier_cookie = compte_fb.get(cle_db2)
                mon_compte = compte_fb.get(cle_db2)
                
                if derniere_page:
                    if derniere_page == name: debut = True
                    if not debut: continue
                
                print("✅", mon_compte); print(name); print(url_page);${codeActionsOptionnelles}`;
            }


let codeFonctionVisiterPage = "";

if (activerVisiterPage) {
let callAmi = activerAmi ? `await ami(fichier2, new_page, url_page)`: "";
codeFonctionVisiterPage = `
async def visiter_page(context, fichier2, url_page):
    try:
        new_page = await context.new_page()
        await new_page.goto(url_page, timeout=0)
        ${callAmi}

    except Exception as e:
        print("cc..")

    finally:
        if new_page:
            await new_page.close()
`;
}


let codeFonctionAmi = "";

if (activerAmi) {

let lignePauseAmi = "";
    if (activerPauseAmiCocher) {
        lignePauseAmi = `
        print("Patiente ${valeurPauseAmi}s"); await asyncio.sleep(${valeurPauseAmi})`;
    }
	
	codeFonctionAmi = `
async def ami(fichier2, new_page, url_page):
    btn_ami = await new_page.query_selector('a[href*="/friends"]')
    if btn_ami: 
        print("ami")
        await mettre_a_jour(fichier2, {"ami": 1}, "page", url_page)
        ${lignePauseAmi}
    else:
        print("pas de btn ami")
        await mettre_a_jour(fichier2, {"ami": 0}, "page", url_page)
`;
}


const codeImports = `import asyncio
from playwright.async_api import async_playwright
from outils_playwright import (charger_fichier_d, verifier_nouveau_element, verifier_date_recontacte, mettre_a_jour, appliquer_stealth, charger_cookies, ajouter_dans_fichier)

${codeFonctionAmi}
${codeFonctionVisiterPage}`;


const codeFonctionPrincipale = `
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
        
        cle_db1 = "${db1}"
        cle_db2 = "${db2}"
        
        fichier1 = "${f1}"
        fichier2 = "${f2}"
        pages_fb = await verifier_nouveau_element(fichier1, fichier2, cle_db1)${ligneFiltrePages}
        
        fichier3 = "${f3}"
        fichier4 = "${f4}"
        comptes_fb = await verifier_nouveau_element(fichier3, fichier4, cle_db2)${ligneFiltreComptes}
        
        fichier_derniere_page = "${f_derniere}"
        derniere_page = (await charger_fichier_d(fichier_derniere_page)).get(cle_db1)${ligneDebutFalse}
        
        index = next((i for i, page in enumerate(pages_fb) if page[cle_db1] == derniere_page), 0)
        page_suivant = None
        pages_deja_contacter = set()
        tour = 0
        
        if len(comptes_fb) == 0: 
            print("Tout les comptes ont été utilisés") 
        
        for compte_fb in comptes_fb:             
            tour += 1
            print("index ", index)${codePreparationCompte}${codeBouclePagesComplete}${codeInterneBoucleIndex}`;

            workflowActif.push({
                id: "standard_imports",
                label: "📦 [Import] asyncio, playwright & outils_playwright",
                code: codeImports,
                uid: Date.now() + Math.random()
            });

            workflowActif.push({
                id: "bloc_standard_variable_lie",
                label: "⚡ [Standard] Fonction main() dynamique",
                code: codeFonctionPrincipale,
                uid: Date.now() + Math.random()
            });

            afficherWorkflow();
        }

        function toutSupprimerWorkflow() {
            workflowActif = [];
            afficherWorkflow();
        }

        function afficherWorkflow() {
            const container = document.getElementById('workflow_actif');
            container.innerHTML = '';

            if (workflowActif.length === 0) {
                container.innerHTML = '<div style="color: #999; padding: 20px; text-align: center;">Le workflow est vide. Configurez vos variables puis injectez votre bloc lié.</div>';
                return;
            }

            workflowActif.forEach((item, index) => {
                const div = document.createElement('div');
                div.className = 'item-workflow';
                const codeEchappe = item.code.replace(/</g, "&lt;").replace(/>/g, "&gt;");

                div.innerHTML = `
                    <div class="item-code">${codeEchappe}</div>
                    <div class="item-actions">
                        <button class="btn-action" onclick="monterLigne(${index})">▲</button>
                        <button class="btn-action" onclick="descendreLigne(${index})">▼</button>
                        <button class="btn-action" style="color: red;" onclick="supprimerLigne(${index})">❌</button>
						
						<button class="btn-action" onclick="editerLigne(${index})">✏️</button>
						<button class="btn-action" onclick="ajouterInstructionDansFonction(${index})">➕</button>
						<button class="btn-action" onclick="editerCodeComplet(${index})">📝</button>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function monterLigne(index) {
            if (index > 0) {
                const temp = workflowActif[index];
                workflowActif[index] = workflowActif[index - 1];
                workflowActif[index - 1] = temp;
                afficherWorkflow();
            }
        }

        function descendreLigne(index) {
            if (index < workflowActif.length - 1) {
                const temp = workflowActif[index];
                workflowActif[index] = workflowActif[index + 1];
                workflowActif[index + 1] = temp;
                afficherWorkflow();
            }
        }

        function supprimerLigne(index) {
            workflowActif.splice(index, 1);
            afficherWorkflow();
        }
		
		
		document.getElementById("bigEditor").addEventListener("input", analyserFonctionsDepuisEditor);
		
		let editorIndex = null;
		function editerCodeComplet(index) {
			editorIndex = index;
			
			const toutLeCode = workflowActif.map(w => w.code).join("\n\n");
			document.getElementById("bigEditor").value = toutLeCode;
			
			analyserFonctionsDepuisEditor();
			document.getElementById("editorModal").style.display = "block";
		}
		
		
		function fermerEditor() {
			document.getElementById("editorModal").style.display = "none";
			editorIndex = null;
		}


		function sauverEditor() {
			const newCode = document.getElementById("bigEditor").value;
			
			if (editorIndex === null) { // SI aucun bloc lié

				workflowActif.push({
					id: "editor_" + Date.now(),
					label: "Code complet",
					code: newCode,
					uid: Date.now()
				});

				fermerEditor();
				afficherWorkflow();
				return;
			}

			workflowActif[editorIndex].code = newCode; // mode édition classique
			const match = newCode.match(/async def\s+(\w+)\((.*?)\)/);

			if (match) {
				workflowActif[editorIndex].label =
					`async def ${match[1]}(${match[2]})`;
			}

			fermerEditor();
			afficherWorkflow();
		}
		
		
		
		function ajouterFonctionDansEditorr() {
			document.getElementById("popupFonction").style.display = "block";
			document.getElementById("popup_func_name").value = "";
			document.getElementById("popup_func_params").value = "";
			document.getElementById("zone_params_popup").style.display = "none";
		}

		function suivantFonctionPopupp() {
			document.getElementById("zone_params_popup").style.display = "block";
		}

		function validerFonctionPopupp() {
			const name = document.getElementById("popup_func_name").value.trim();
			const params = document.getElementById("popup_func_params").value.trim();

			const nouvelleFonction = `
		async def ${name}(${params}):

		`;

			const editor = document.getElementById("bigEditor");
			const codeActuel = editor.value;
			const nouveauCode = insererFonctionAvantPremiereFonction(codeActuel, nouvelleFonction);

			editor.value = nouveauCode;
			analyserFonctionsDepuisEditor();
			document.getElementById("popupFonction").style.display = "none";
		}


        function afficherToast(message, isError = false) {
            const toast = document.getElementById("toast");
            toast.innerText = message;
            if (isError) {
                toast.classList.add("error");
            } else {
                toast.classList.remove("error");
            }
            toast.classList.add("visible");
            
            setTimeout(() => {
                toast.classList.remove("visible");
            }, 2000);
        }

        function envoyerConfiguration() {
            const nomFichier = document.getElementById('fichier_destination').value;
            if (workflowActif.length === 0) {
                afficherToast("Erreur : Le workflow est vide !", true);
                return;
            }

            const etapesCode = workflowActif.map(item => item.code);

            fetch('/generer-workflow-universel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fichier: nomFichier, etapes: etapesCode })
            })
            .then(res => {
                if(res.ok) {
                    afficherToast("Fichier Python généré avec succès !");
                } else {
                    afficherToast("Erreur lors de la génération du fichier.", true);
                }
            })
            .catch(err => {
                afficherToast("Erreur réseau de communication.", true);
            });
        }
		
		function editerLigne(index) {
			const item = workflowActif[index];

			let ancienNom = item.label.match(/async def (\w+)/)?.[1] || "";
			let anciensParams = item.label.match(/\((.*)\)/)?.[1] || "";

			const nouveauNom = prompt("Nom de la fonction :", ancienNom);
			if (nouveauNom === null) return;

			const nouveauxParams = prompt("Paramètres :", anciensParams);
			if (nouveauxParams === null) return;

			const nomFinal = nouveauNom.trim() || ancienNom;
			const paramsFinal = nouveauxParams.trim() || anciensParams;

			const code = `
		async def ${nomFinal}(${paramsFinal}):
			pass
		`;

			//workflowActif[index].id = "user_" + nomFinal;
			workflowActif[index].id = nomFinal;
			workflowActif[index].label = `async def ${nomFinal}(${paramsFinal})`;
			workflowActif[index].code = code;

			afficherWorkflow();
		}

        window.onload = function() {
            genererBibliotheque();
            afficherWorkflow();
        };
		