# Reprise de la collecte (2e passage) — accès réseau ouvert, recherche Web épuisée

Contexte : au premier passage, le réseau du conteneur bloquait tous les sites; les agents n'ont lu que des extraits de moteur de recherche. **Le réseau est maintenant ouvert.** En revanche, le quota de l'outil WebSearch est épuisé pour ce tour.

## Règles de ce passage

1. Lis d'abord `MANDAT-COMMUN.md` (règles, définitions, format JSON) dans ce dossier, puis le fichier de collecte existant indiqué dans ton mandat (pistes, URL, montants à confirmer).
2. **N'utilise pas WebSearch** et n'interroge **aucun moteur de recherche généraliste** (Google, Bing, DuckDuckGo, etc.), ni directement ni par curl, ni par un service de lecture, un mandataire ou une archive tierce. Tu peux :
   - ouvrir directement les URL déjà repérées dans le fichier de collecte;
   - naviguer dans les sites officiels (municipalité, MRC, chambre, organisme de développement économique) : pages d'index, listes de procès-verbaux, pages « liste des contrats », « rapports financiers », « rapport annuel », et suivre leurs liens;
   - utiliser `curl -sSL -A "Mozilla/5.0" -o <fichier> <url>` (téléchargement direct) ou WebFetch. Télécharge les PDF dans un dossier neuf sous `/tmp/claude-0/<ton-nom>/` et extrais-les avec `pdftotext -layout`; lance tout Python avec `python3 -I`.
3. Pour chaque montant déjà inscrit au premier passage : **confirme-le à la source primaire** (montant, année, payeur, catégorie, taxes incluses ou non) et ajuste la confiance. Un montant qui ne se confirme pas reste avec confiance « faible » et une remarque.
4. Ajoute les nouveaux versements trouvés. Garde `sources_consultees_sans_resultat` à jour.
5. **Réécris le fichier de collecte** indiqué (même chemin, même format), en conservant les informations utiles du premier passage. Écris après chaque étape importante.
6. Si un site refuse les téléchargements (403, protection anti-robot), essaie WebFetch; si les deux échouent, note-le et passe à autre chose.
7. Message final court (moins de 250 mots) : montants confirmés, nouveaux montants, ce qui reste à valider.
