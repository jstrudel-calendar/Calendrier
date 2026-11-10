# Méthodologie — financement municipal des chambres de commerce au Québec

Date des travaux : 10 novembre 2026. Fichiers : `tableau-comparatif.xlsx`, `donnees-brutes.json`, `resultats.json`, `calculs.py`, dossier `collecte/` (mandats des agents, fichiers bruts de collecte, script d'extraction StatCan, décisions de normalisation).

## 1. Définitions

**Numérateur.** Somme versée à la chambre par une municipalité, une MRC, une agglomération ou un organisme municipal de développement économique, classée en :
A fonctionnement (partenariat annuel, entente de base); B projets ou mandats; C commandites d'événements (incluant l'achat de tables et de billets); D cotisation de membre; E contribution en nature.
Indicateur principal = A + B + C. Indicateur restreint = A. D et E sont notés mais exclus.
Exclusions : argent provincial ou fédéral, même géré par une ville ou une MRC (ex. Fonds régions et ruralité – FRR). Un versement d'ID Gatineau financé par le FRR (50 000 $, 2024) est ainsi exclu.

**Dénominateur.** Emplacements d'entreprises **avec employés**, Statistique Canada, tableau 33-10-1097-01, **décembre 2025**, par subdivision de recensement (municipalité). Une seule source et une seule période pour toutes les chambres. Population : Recensement 2021 (98-10-0002-01). Détails et limites : `collecte/phase2-sources.md`.
Le **total des emplacements (avec et sans employés)** n'existe pas par municipalité dans les tableaux publics (le tableau « sans employés » n'est publié que pour le Canada et les provinces). La colonne secondaire est donc vide.

**Indicateurs.** $/entreprise/année = moyenne annuelle (A+B+C) ÷ entreprises avec employés; idem pour A seulement; $/habitant/année à titre de contrôle. Ratios arrondis à deux décimales, montants au dollar.

## 2. Règles de calcul

- Fenêtre de référence : exercices 2023, 2024 et 2025.
- Un versement pluriannuel est réparti également sur ses années (montant ÷ nombre d'années). Exemple : 335 482 $ pour 2022-2023 = 167 741 $ par an; seule la tranche 2023 entre dans la période.
- Moyenne annuelle = somme des tranches tombant dans les **années observées** ÷ nombre d'années observées. Les années observées sont fixées par chambre selon les documents réellement consultés :
  - CCILaval, CCIQ, CCG : 2023-2025;
  - CCIM : 2023-2024 (la contribution 2025 de la MRC n'est pas connue);
  - CCISF : 2025 seulement (seule année où les listes des deux payeurs ont été lues);
  - CCI3R et CCMM : années couvertes par le seul versement connu.
- Les montants sont pris tels que publiés : taxes incluses quand la source l'indique (CCI3R, MRC du Fjord-du-Saguenay), sinon non précisé.
- Une année « observée » sans versement trouvé compte pour 0 : chaque moyenne est un **plancher**, sauf si la couverture documentaire de la chambre est complète.
- **Confiance globale** d'une chambre : « élevée » si au moins 80 % du total vient de montants de confiance élevée; « moyenne » si au moins 80 % vient de montants élevée ou moyenne; sinon « faible ». Les statistiques descriptives n'utilisent que les chambres de confiance élevée ou moyenne.

## 3. Hypothèses de territoire

| Chambre | Municipalités retenues | Hypothèse |
|---|---|---|
| CCILaval | Laval | Ville-MRC |
| CCIQ | Québec, L'Ancienne-Lorette, Saint-Augustin-de-Desmaures | Agglomération de Québec (territoire revendiqué non vérifié) |
| CCIRS | 5 villes de l'agglomération de Longueuil et 6 de la MRC de Marguerite-D'Youville | Site de la CCIRS; Saint-Bruno-de-Montarville et Sainte-Julie ajoutées en août 2024 (on garde le territoire actuel) |
| CCG | Gatineau | Ville-MRC |
| CCIGL | Lévis | Ville-MRC; « Grand Lévis » pourrait déborder |
| CCIS | Sherbrooke | Non confirmé |
| CCISF | Saguenay et 12 municipalités de la MRC du Fjord-du-Saguenay publiées par StatCan | Mémoire de la CCISF |
| CCI3R | Trois-Rivières | Ville-MRC |
| CCIM | Terrebonne, Mascouche | MRC Les Moulins |
| CCMM | 15 municipalités publiées de l'agglomération de Montréal | La CCMM se dit « du grand Montréal »; hypothèse prudente |

## 4. Seuils de taille

Seuils conservés tels que demandés : très grand (20 000 et plus), grand (8 000 à 19 999), moyen (3 000 à 7 999), petit (1 000 à 2 999), très petit (moins de 1 000). Dans l'échantillon chiffré, aucune chambre « petite » ou « très petite » n'a de montant. Ajuster les seuils n'aurait donc rien changé à l'analyse.

## 5. Grille de comparabilité (sur 100)

| Critère | Poids | Règle |
|---|---|---|
| Entreprises avec employés | 35 | Pleins points entre 0,5 et 1,5 fois Laval (6 827 à 20 481). Décroissance logarithmique jusqu'à 0 à 0,25 ou 3 fois Laval |
| Population | 20 | Même règle |
| Territoire | 20 | Une seule municipalité = 100 %; plusieurs municipalités dont une ≥ 80 % de la population = 60 %; 50 à 80 % = 30 %; sinon 0 |
| Contexte métropolitain | 15 | Banlieue de la RMR de Montréal, ou ville adossée à un pôle plus grand (Gatineau, Lévis) = 100 %; banlieue d'une autre RMR = 60 %; ville centrale d'une RMR = 50 %; Montréal = 30 %; centre d'une agglomération de recensement = 20 %; hors RMR = 0 |
| Structure économique | 10 | Part des emplacements avec employés en construction, fabrication, commerce de gros, transport et entreposage (SCIAN 23, 31-33, 41, 48-49), même tableau StatCan. Pleins points si l'écart avec Laval est d'au plus 3 points de pourcentage, 0 à 10 points |

Classement : « Oui, forte » à 70 et plus; « Oui, partielle » de 50 à 69. La décroissance graduée (plutôt qu'un seuil binaire à ±50 %) évite qu'une chambre à 49 % d'écart obtienne tout et une chambre à 51 % rien.
La grille a été appliquée aux 10 chambres de grandes villes documentées. Les autres chambres sont trop petites pour atteindre 50 : à 0,25 fois Laval ou moins, elles n'ont aucun point sur la taille.

## 6. Déroulement et vérification

1. **Premier passage (agents).** Une vingtaine de sous-agents, un par phase, grande ville et groupe de régions. Le réseau de la session bloquait alors tous les sites et le quota de recherche Web s'est épuisé : collecte très partielle, fondée sur des extraits de moteur de recherche.
2. **Accès réseau ouvert, second passage.** Il a été interrompu par la limite d'utilisation. L'orchestrateur a alors téléchargé et lu lui-même les documents primaires pour les comparables :
   - listes de contrats de Québec 2023 à 2025;
   - tableaux du fonds de projets de Gatineau 2023 à 2025 et rapport FRR 2024;
   - listes de Saguenay 2024-2025 et de la MRC du Fjord-du-Saguenay 2023 et 2025;
   - procès-verbaux de la MRC Les Moulins;
   - rapports d'activités de la CCIRS, de la CCIQ et de la CCI3R.
3. **Sites non consultables.** laval.ca et le site de documents de Trois-Rivières renvoient une page de contrôle anti-robot. Elle n'a pas été contournée. Les montants de Laval et de Trois-Rivières restent donc de confiance moyenne.
4. **Vérification indépendante (phase 5).** Un agent qui n'a pas participé à la collecte a revérifié tous les montants des comparables et l'arithmétique. Résultats : `collecte/phase5-verification.json` et section 8.
5. **Contrôle du classeur.** Recalculé dans LibreOffice : les formules concordent avec le script (0 écart) et aucune cellule n'est en erreur.

## 7. Couverture

- **Chambres répertoriées** : environ 100 (inventaire partiellement vérifié; le réseau de la FCCQ en compte près de 125).
- **Chambres traitées en profondeur** : 10, celles des grandes villes.
- **Avec au moins un montant municipal retenu** : 7, dont 6 de confiance élevée ou moyenne.
- **Taux de couverture** : 6/100, soit environ 6 %. Pour l'échantillon des grandes villes : 6/10.
- **Sans montant, sur le territoire des grandes villes** : CCIRS (Longueuil), CCIGL (Lévis), CCIS (Sherbrooke). L'absence de montant traduit une recherche incomplète, pas une absence de financement.

## 8. Résultats de la vérification (phase 5)

Échantillon : 11 montants sur 26, soit 42 %, dont tous ceux des comparables chiffrés, plus l'arithmétique des 7 chambres chiffrées. Détail : `collecte/phase5-verification.json`.

**Confirmés à la source :**
- Québec, 25 000 $ (2025);
- Gatineau, 70 000 $ (2024);
- MRC Les Moulins, 113 300 $ (2023) et 64 000 $ (2024; c'est un montant maximum autorisé);
- Saguenay, 25 000 $ (2025);
- MRC du Fjord-du-Saguenay, 43 730 $ (2025);
- Symbiose Laval, 151 460 $ (argent municipal, catégorie B).

**Écarts et éléments non vérifiables :**
- **CCILaval, 200 000 $ (Achat local).** La citation attribuée au communiqué de la CCILaval du 25 novembre 2024 n'y figure pas : le communiqué nomme « Laval économique / Ville de Laval » sans montant. Le montant ne repose plus que sur l'extrait de la résolution CM-20240604-590. Il est maintenu en confiance moyenne, avec une analyse de sensibilité : sans ce montant, le ratio de Laval passe de 16,68 $ à 11,80 $.
- **CCILaval, 335 482 $ et 265 000 $.** Non vérifiables, car laval.ca est bloqué. La catégorie de l'entente de 265 000 $ est indéterminée (A possible).
- **Trois-Rivières, 48 864,38 $.** Non vérifiable (site bloqué). Sur 6 ans plutôt que 5, le ratio passerait de 2,41 $ à 2,01 $.

**Arithmétique.** Les 7 totaux et ratios concordent. Le vérificateur signale que les années observées de la CCISF et de la CCIM sont fixées à la main (section 2). Avec la règle par défaut, la CCISF serait à 9,87 $ et la CCIM à 12,37 $. L'écart est présenté comme sensibilité dans le rapport.
