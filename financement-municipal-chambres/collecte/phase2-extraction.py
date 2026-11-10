#!/usr/bin/env python3
"""Phase 2 — dénominateurs par subdivision de recensement (SDR) du Québec.

Sources (Statistique Canada, fichiers CSV « tableau complet », version française) :
  - 33-10-1097-01 Nombre d'entreprises canadiennes, avec employés, RMR et SDR, décembre 2025
    https://www150.statcan.gc.ca/n1/tbl/csv/33101097-fra.zip   (DOI 10.25318/3310109701-fra)
  - 98-10-0002-01 Chiffres de population et des logements : Canada et SDR (municipalités), Recensement 2021
    https://www150.statcan.gc.ca/n1/tbl/csv/98100002-fra.zip   (DOI 10.25318/9810000201-fra)
  - 98-10-0007-01 Chiffres de population et des logements : Canada et divisions de recensement (noms des DR)
    https://www150.statcan.gc.ca/n1/tbl/csv/98100007-fra.zip

Usage : python3 -I phase2-extraction.py <dossier contenant t1097/ t0002/ t0007/>
Aucune valeur n'est estimée : une cellule vide = SDR non publiée dans la source.
"""
import csv, sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(__file__).resolve().parent
csv.field_size_limit(10**9)

def lire(p):
    with open(p, encoding="utf-8-sig") as f:
        yield from csv.reader(f, delimiter=";")

# Noms des divisions de recensement (MRC ou territoire équivalent)
dr = {}
for r in lire(src / "t0007/98100007.csv"):
    if len(r) > 2 and r[2].startswith("2021A000324"):
        dr[r[2][-4:]] = r[1]

# Population et superficie 2021 par SDR
pop = {}
it = lire(src / "t0002/98100002.csv")
h = next(it)
i_pop = next(i for i, c in enumerate(h) if "Population, 2021" in c)
i_sup = next(i for i, c in enumerate(h) if "Superficie des terres" in c)
for r in it:
    if len(r) > 2 and r[2].startswith("2021A000524"):
        pop[r[2][-7:]] = (r[1], r[i_pop], r[i_sup])

# Entreprises avec employés, décembre 2025
SECT = {"Total, toutes les industries [1]": "total_avec_employes", "Construction [23]": "scian_23",
        "Fabrication [31-33]": "scian_31_33", "Commerce de gros [41]": "scian_41",
        "Transport et entreposage [48-49]": "scian_48_49"}
cbc = {}
periode = ""
for r in lire(src / "t1097/33101097.csv"):
    if len(r) < 12 or not r[2].startswith("2021A000524") or r[3] != "Total, avec employés":
        continue
    k = SECT.get(r[4])
    if k:
        periode = r[0]
        cbc.setdefault(r[2][-7:], {"nom": r[1]})[k] = r[11]

with open(out / "phase2-denominateurs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["code_sdr", "nom_municipalite", "type_sdr", "code_dr", "nom_dr_ou_mrc", "entreprises_avec_employes",
                "total_emplacements", "periode_cbc", "population_2021", "superficie_km2", "population_recente",
                "annee_population_recente"])
    for code in sorted(set(pop) | set(cbc)):
        nom, p, s = pop.get(code, (cbc.get(code, {}).get("nom", ""), "", ""))
        e = cbc.get(code, {}).get("total_avec_employes", "")
        w.writerow([code, nom, "", code[:4], dr.get(code[:4], ""), e, "",
                    "décembre 2025 (réf. " + periode + ")" if e else "non publiée", p, s, "", ""])

with open(out / "phase2-structure-economique.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    cols = ["total_avec_employes", "scian_23", "scian_31_33", "scian_41", "scian_48_49"]
    w.writerow(["code_sdr", "nom_municipalite"] + cols)
    for code in sorted(cbc):
        w.writerow([code, cbc[code]["nom"]] + [cbc[code].get(c, "") for c in cols])
print(len(pop), "SDR recensement;", len(cbc), "SDR CBC; période", periode)
