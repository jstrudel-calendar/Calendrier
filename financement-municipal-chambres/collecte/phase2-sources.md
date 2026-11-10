# Phase 2 — Dénominateurs par municipalité (SDR) du Québec : sources

Date de consultation et d'extraction : 2026-11-10. Extraction réalisée par l'orchestrateur (téléchargement direct des tableaux complets), script `phase2-extraction.py`.

## Sources retenues (une seule source et une seule période pour toutes les chambres)

| Donnée | Tableau | Période | URL |
|---|---|---|---|
| Emplacements d'entreprises **avec employés**, total et par secteur SCIAN | Statistique Canada, **33-10-1097-01** « Nombre d'entreprises canadiennes, avec employés, régions métropolitaines de recensement et subdivisions de recensement, décembre 2025 » (DOI 10.25318/3310109701-fra) | décembre 2025 (période de référence codée 2025-07 dans le fichier) | https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=3310109701 |
| Population 2021 et superficie des terres (km²) | Statistique Canada, **98-10-0002-01** « Chiffres de population et des logements : Canada et subdivisions de recensement (municipalités) », Recensement 2021 | 2021 | https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=9810000201 |
| Noms des divisions de recensement (MRC ou territoire équivalent) | Statistique Canada, **98-10-0007-01** | 2021 | https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=9810000701 |

## Notes de méthode

- **Unité** : l'emplacement statistique (établissement) inscrit au Registre des entreprises, et non l'entreprise juridique. Une entreprise ayant plusieurs établissements dans des municipalités différentes est comptée dans chacune.
- **Couverture** : 1 051 des 1 282 SDR du Québec sont publiées dans 33-10-1097-01. Les 231 SDR absentes sont de petites municipalités (37 015 habitants au total, soit moins de 0,5 % de la population) : Statistique Canada ne publie pas les SDR hors RMR qui comptent moins de 10 entreprises avec employés. Leur absence fait légèrement sous-estimer le dénominateur de quelques chambres rurales; elle est sans effet pour Laval et les comparables.
- **Total des emplacements (avec et sans employés)** : **non disponible** à l'échelle municipale. Le tableau « sans employés » de décembre 2025 (33-10-1096-01) n'est publié que pour le Canada et les provinces; aucun tableau public ne le ventile par SDR. La colonne secondaire « ratio sur le total des emplacements » est donc laissée vide. Ce n'est pas une estimation manquante : la donnée n'existe pas en accès libre (elle serait accessible par demande de totalisation spéciale).
- **Population** : Recensement 2021 (une seule source pour tous). Aucune estimation plus récente n'a été ajoutée, pour éviter de mélanger les sources.
- **Structure économique** : emplacements avec employés en construction (SCIAN 23), fabrication (31-33), commerce de gros (41) et transport et entreposage (48-49), même tableau, même période; fichier `phase2-structure-economique.csv`.
- **Noms de DR** : noms officiels du Recensement 2021 (ex. Trois-Rivières est dans la DR « Francheville », Saguenay dans « Le Saguenay-et-son-Fjord »).
- **Valeurs clés** (vérification) : Laval 13 654 entreprises avec employés, 438 366 habitants (2021), 246,13 km².

## Reproduire

```
mkdir -p /tmp/denom && cd /tmp/denom
for t in 33101097 98100002 98100007; do curl -sSO https://www150.statcan.gc.ca/n1/tbl/csv/$t-fra.zip; done
unzip -q 33101097-fra.zip -d t1097; unzip -q 98100002-fra.zip -d t0002; unzip -q 98100007-fra.zip -d t0007
cd / && python3 -I <chemin>/collecte/phase2-extraction.py /tmp/denom
```
