# Phase 6 — relance ciblée et élargissement (11 novembre 2026)

Lis d'abord `MANDAT-COMMUN.md` (règles, définitions A/B/C/D/E, format JSON) dans ce dossier. Le présent document le complète et a priorité en cas de conflit.

## Leçons des passages précédents (à appliquer)

- **Les listes de contrats ne montrent pas les subventions.** Une ville peut verser une subvention ou une contribution à une chambre par résolution (comité exécutif, conseil) sans qu'elle figure dans la liste des contrats. Cherche **les deux** : listes de contrats (art. 477.6 LCV, 961.4 CM) **et** résolutions ou procès-verbaux (« aide financière », « contribution », « subvention », « partenariat », « entente »).
- **Le payeur est souvent la MRC**, pas la ville (ex. MRC Les Moulins, MRC du Fjord-du-Saguenay). Cherche aussi dans les procès-verbaux et listes de contrats de la MRC.
- **Fonds provinciaux** (Fonds régions et ruralité – FRR, FDT, MEIE) gérés par une MRC ou une ville : à noter, mais avec `"inclus": false` et un motif. Si un procès-verbal impute la dépense à un poste budgétaire de la MRC sans mentionner de fonds provincial, c'est municipal.
- Les **états financiers ou rapports annuels des chambres** donnent parfois la ligne « subventions municipales » : c'est la meilleure source quand elle existe.

## Outils et économie

- **Budget : 20 WebSearch au maximum** pour tout ton mandat (le quota est partagé entre les agents). Privilégie le téléchargement direct (`curl -sSL -A Mozilla/5.0 -o <fichier> <url>`) des documents trouvés, dans un dossier neuf sous `/tmp/claude-0/<ton-nom>/`, puis `pdftotext -layout` et `grep -i -n "chambre de commerce"`. Lance tout Python avec `python3 -I`.
- Si un site renvoie une page anti-robot (« Just a moment », 403), **ne la contourne pas** : note « accès bloqué » et passe à autre chose. N'interroge pas de moteur de recherche par curl.
- Ne contacte personne et ne remplis aucun formulaire.
- Travaille vite : une chambre ne doit pas prendre plus de 4 ou 5 recherches. Si rien ne sort, documente ce que tu as consulté et passe à la suivante.

## Format de sortie

Le format JSON commun, avec ces champs ajoutés à chaque objet chambre :

- `"nb_membres"` (nombre ou null) et `"source_nb_membres"` (URL ou extrait, avec l'année);
- `"codes_sdr"` : codes à 7 chiffres des municipalités du territoire, pris dans `phase2-denominateurs.csv` (même dossier; colonne `code_sdr`);
- pour chaque versement : `"annee_debut"` et `"annee_fin"` (entiers) en plus de `annee_ou_periode`;
- `"couverture_documentaire"` : une phrase disant quelles années et quels payeurs ont été réellement vérifiés (ex. « Ville : listes de contrats 2023-2025 et PV du conseil 2024; MRC : PV 2023-2025 »).

Écris ton fichier après chaque chambre. Message final court (moins de 200 mots) : chambres traitées, montants trouvés et confiance, ce qui reste à valider.
