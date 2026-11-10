#!/usr/bin/env python3
"""
Financement municipal des chambres de commerce au Québec — calculs et classeur.

Usage :
    python3 calculs.py consolider   # collecte/*.json + collecte/normalisation.json + dénominateurs -> donnees-brutes.json
    python3 calculs.py calculer     # donnees-brutes.json -> resultats.json + tableau-comparatif.xlsx
    python3 calculs.py              # les deux

Toutes les règles de calcul sont ici (voir methodologie.md) :
- fenêtre de référence 2023-2025;
- un versement pluriannuel est réparti également sur ses années (montant / nb_annees_couvertes);
- la moyenne annuelle d'une chambre = somme des montants annualisés tombant dans les années observées
  / nombre d'années observées (années 2023-2025 couvertes par au moins un versement A, B ou C retenu);
  si aucun versement retenu ne tombe dans 2023-2025, on utilise l'année la plus récente disponible (signalé);
- indicateur principal = A + B + C; indicateur restreint = A; D et E exclus;
- ratios arrondis à 2 décimales, montants au dollar.
"""
import csv
import json
import math
import statistics
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
COLLECTE = ICI / "collecte"
BRUTES = ICI / "donnees-brutes.json"
RESULTATS = ICI / "resultats.json"
XLSX = ICI / "tableau-comparatif.xlsx"

FENETRE = (2023, 2025)
CATS_INDICATEUR = ("A", "B", "C")
RANG_CONF = {"élevée": 3, "moyenne": 2, "faible": 1}
LAVAL_ID = "ccilaval"

# Seuils de taille (entreprises avec employés) — voir methodologie.md
SEUILS_TAILLE = [
    (20000, "Très grand (20 000 et plus)"),
    (8000, "Grand (8 000 à 19 999)"),
    (3000, "Moyen (3 000 à 7 999)"),
    (1000, "Petit (1 000 à 2 999)"),
    (0, "Très petit (moins de 1 000)"),
]

# Grille de comparabilité (poids sur 100)
POIDS = {
    "entreprises": 35,
    "population": 20,
    "territoire": 20,
    "contexte": 15,
    "structure": 10,
}
POINTS_CONTEXTE = {
    "banlieue_rmr_montreal": 1.0,      # ville de banlieue de la RMR de Montréal (comme Laval)
    "voisine_pole_plus_grand": 1.0,    # ville d'une RMR adossée à un pôle plus grand (Lévis, Gatineau)
    "centre_rmr": 0.5,                 # ville centrale d'une RMR (Québec, Sherbrooke, Saguenay, Trois-Rivières)
    "metropole": 0.3,                  # Montréal (pôle lui-même)
    "banlieue_autre_rmr": 0.6,         # banlieue d'une autre RMR
    "agglomeration_ar": 0.2,           # ville centre d'une agglomération de recensement
    "hors_rmr": 0.0,
}


# ---------------------------------------------------------------- utilitaires
def lire_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def ecrire_json(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def entier(x):
    if x in (None, ""):
        return None
    try:
        return int(float(str(x).replace(" ", "").replace(" ", "").replace(",", ".")))
    except ValueError:
        return None


def flottant(x):
    if x in (None, ""):
        return None
    try:
        return float(str(x).replace(" ", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def categorie_taille(n):
    if n is None:
        return "Indéterminée"
    for seuil, nom in SEUILS_TAILLE:
        if n >= seuil:
            return nom
    return SEUILS_TAILLE[-1][1]


# ---------------------------------------------------------------- consolidation
def charger_denominateurs():
    p = COLLECTE / "phase2-denominateurs.csv"
    rows = {}
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[str(r["code_sdr"]).strip()] = r
    return rows


def charger_structure():
    p = COLLECTE / "phase2-structure-economique.csv"
    if not p.exists():
        return {}
    out = {}
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[str(r["code_sdr"]).strip()] = r
    return out


def consolider():
    """Fusionne les fichiers de collecte selon collecte/normalisation.json.

    normalisation.json = {
      "chambres": [ {"id", "fichier", "nom_source", "chambre", "codes_sdr": [...],
                     "contexte": clé de POINTS_CONTEXTE, "region_administrative", "remarques_orchestrateur"} ],
      "versements": { "<id>|<index>": {"annee_debut", "annee_fin", "inclus", "motif_exclusion",
                                       "categorie" (si reclassé), "montant" (si corrigé), "verification", "confiance"} },
      "ajouts": { "<id>": [versements supplémentaires au format commun + champs normalisés] }
    }
    """
    norm = lire_json(COLLECTE / "normalisation.json")
    denom = charger_denominateurs()
    struct = charger_structure()
    cache = {}
    chambres = []
    for c in norm["chambres"]:
        fichier = COLLECTE / c["fichier"]
        if fichier not in cache:
            data = lire_json(fichier)
            cache[fichier] = [d for d in data if isinstance(d, dict) and "chambre" in d]
        src = next((d for d in cache[fichier] if d["chambre"] == c["nom_source"]), None)
        if src is None:
            raise SystemExit(f"Chambre introuvable dans {c['fichier']}: {c['nom_source']}")
        versements = []
        for i, v in enumerate(src.get("versements", []) + norm.get("ajouts", {}).get(c["id"], [])):
            cle = f"{c['id']}|{i}"
            n = norm["versements"].get(cle, {})
            v2 = dict(v)
            v2.update({k: n[k] for k in n})
            v2.setdefault("inclus", v2.get("categorie") in CATS_INDICATEUR)
            v2["cle"] = cle
            versements.append(v2)
        manquants = [s for s in c["codes_sdr"] if s not in denom]
        if manquants:
            print(f"AVERTISSEMENT {c['id']}: SDR absentes des dénominateurs {manquants}")
        chambres.append({
            "id": c["id"],
            "chambre": c.get("chambre", src["chambre"]),
            "site_web": src.get("site_web", ""),
            "region_administrative": c.get("region_administrative", src.get("region_administrative", "")),
            "municipalites_desservies": c.get("municipalites_desservies", src.get("municipalites_desservies", [])),
            "hypothese_territoire": src.get("hypothese_territoire", ""),
            "codes_sdr": c["codes_sdr"],
            "contexte": c["contexte"],
            "statut_collecte": src.get("statut", ""),
            "sources_consultees_sans_resultat": src.get("sources_consultees_sans_resultat", []),
            "remarques_orchestrateur": c.get("remarques_orchestrateur", ""),
            "fichier_collecte": c["fichier"],
            "versements": versements,
        })
    brutes = {
        "meta": norm.get("meta", {}),
        "chambres": chambres,
        "denominateurs": [denom[k] for k in sorted(denom)],
        "structure_economique": [struct[k] for k in sorted(struct)],
        "verification": norm.get("verification", {}),
        "inventaire_non_couvert": norm.get("inventaire_non_couvert", []),
    }
    ecrire_json(BRUTES, brutes)
    print(f"{BRUTES.name} : {len(chambres)} chambres")


# ---------------------------------------------------------------- calculs
def annees_versement(v):
    d, f = entier(v.get("annee_debut")), entier(v.get("annee_fin"))
    if d is None:
        return []
    if f is None:
        f = d
    return list(range(d, f + 1))


def apport_annuel(v):
    n = entier(v.get("nb_annees_couvertes")) or 1
    return float(v["montant"]) / n


def calculer_chambre(c, denom, struct):
    retenus = [v for v in c["versements"] if v.get("inclus") and v.get("categorie") in CATS_INDICATEUR
               and flottant(v.get("montant")) is not None]
    in_window = lambda y: FENETRE[0] <= y <= FENETRE[1]
    obs = sorted({y for v in retenus for y in annees_versement(v) if in_window(y)})
    hors_fenetre = False
    if not obs and retenus:
        derniere = max(y for v in retenus for y in annees_versement(v)) if any(annees_versement(v) for v in retenus) else None
        if derniere is not None:
            obs = [derniere]
            hors_fenetre = True
    par_cat = {k: 0.0 for k in CATS_INDICATEUR}
    for v in retenus:
        ans = [y for y in annees_versement(v) if y in obs]
        part = apport_annuel(v) * len(ans) / len(obs) if obs else 0.0
        v["nb_annees_dans_periode_retenue"] = len(ans)
        v["contribution_moyenne_annuelle"] = part
        par_cat[v["categorie"]] += part
    for v in c["versements"]:
        v.setdefault("nb_annees_dans_periode_retenue", 0)
        v.setdefault("contribution_moyenne_annuelle", 0.0)
        v["nb_annees_observees_chambre"] = len(obs)

    pop = ent = tot = 0
    complet = True
    for s in c["codes_sdr"]:
        r = denom.get(s)
        if not r or entier(r.get("entreprises_avec_employes")) is None:
            complet = False
            continue
        ent += entier(r["entreprises_avec_employes"])
        tot += entier(r.get("total_emplacements")) or 0
        pop += entier(r.get("population_2021")) or 0
    if not complet or ent == 0:
        ent = ent or None
    total = sum(par_cat.values())

    # confiance globale : part du total provenant de montants de confiance élevée / moyenne
    if total > 0:
        part_el = sum(v["contribution_moyenne_annuelle"] for v in retenus if v.get("confiance") == "élevée") / total
        part_em = sum(v["contribution_moyenne_annuelle"] for v in retenus if v.get("confiance") in ("élevée", "moyenne")) / total
        conf = "élevée" if part_el >= 0.8 else ("moyenne" if part_em >= 0.8 else "faible")
    else:
        conf = "aucune donnée"

    # structure économique : part des emplacements avec employés en construction, fabrication, gros, transport
    s_num = s_den = 0
    s_ok = True
    for s in c["codes_sdr"]:
        r = struct.get(s)
        if not r:
            s_ok = False
            break
        num = sum(entier(r.get(k)) or 0 for k in ("scian_23", "scian_31_33", "scian_41", "scian_48_49"))
        den = entier(r.get("total_avec_employes"))
        if not den:
            s_ok = False
            break
        s_num += num
        s_den += den
    part_struct = s_num / s_den if s_ok and s_den else None

    # composition du territoire
    pops = [entier(denom[s].get("population_2021")) or 0 for s in c["codes_sdr"] if s in denom]
    part_principale = max(pops) / sum(pops) if pops and sum(pops) else None

    return {
        "id": c["id"],
        "chambre": c["chambre"],
        "region_administrative": c["region_administrative"],
        "municipalites_desservies": c["municipalites_desservies"],
        "nb_municipalites": len(c["codes_sdr"]),
        "part_population_ville_principale": part_principale,
        "population": pop or None,
        "entreprises_avec_employes": ent,
        "total_emplacements": tot or None,
        "denominateur_complet": complet,
        "A": round(par_cat["A"]), "B": round(par_cat["B"]), "C": round(par_cat["C"]),
        "total_ABC": round(total),
        "ratio_ABC": round(total / ent, 2) if ent and total else (0.0 if ent and retenus == [] and False else None),
        "ratio_A": round(par_cat["A"] / ent, 2) if ent and total else None,
        "ratio_hab": round(total / pop, 2) if pop and total else None,
        "ratio_ABC_total_emplacements": round(total / tot, 2) if tot and total else None,
        "periode": (f"{obs[0]}–{obs[-1]}" if len(obs) > 1 else (str(obs[0]) if obs else "")) + (" (hors fenêtre)" if hors_fenetre else ""),
        "annees_observees": obs,
        "hors_fenetre": hors_fenetre,
        "confiance": conf,
        "statut_collecte": c["statut_collecte"],
        "contexte": c["contexte"],
        "part_structure": part_struct,
        "categorie_taille": categorie_taille(ent),
    }


def score_taille(x, ref):
    """Pleins points si 0,5×ref ≤ x ≤ 1,5×ref; décroissance linéaire (échelle log) jusqu'à 0 à 0,25×ref ou 3×ref."""
    if not x or not ref:
        return None
    r = x / ref
    if 0.5 <= r <= 1.5:
        return 1.0
    if r < 0.5:
        return max(0.0, 1 - (math.log(0.5) - math.log(r)) / (math.log(0.5) - math.log(0.25)))
    return max(0.0, 1 - (math.log(r) - math.log(1.5)) / (math.log(3) - math.log(1.5)))


def score_territoire(n, part):
    if n == 1:
        return 1.0
    if part is None:
        return None
    if part >= 0.8:
        return 0.6
    if part >= 0.5:
        return 0.3
    return 0.0


def score_structure(s, ref):
    """Pleins points si écart ≤ 3 points de pourcentage; 0 à 10 points ou plus."""
    if s is None or ref is None:
        return None
    e = abs(s - ref) * 100
    return 1.0 if e <= 3 else max(0.0, 1 - (e - 3) / 7)


def comparabilite(res):
    lav = next(r for r in res if r["id"] == LAVAL_ID)
    for r in res:
        sc = {
            "entreprises": score_taille(r["entreprises_avec_employes"], lav["entreprises_avec_employes"]),
            "population": score_taille(r["population"], lav["population"]),
            "territoire": score_territoire(r["nb_municipalites"], r["part_population_ville_principale"]),
            "contexte": POINTS_CONTEXTE.get(r["contexte"]),
            "structure": score_structure(r["part_structure"], lav["part_structure"]),
        }
        pts = {k: (None if v is None else round(v * POIDS[k], 1)) for k, v in sc.items()}
        dispo = sum(POIDS[k] for k, v in pts.items() if v is not None)
        brut = sum(v for v in pts.values() if v is not None)
        r["score_detail"] = pts
        r["score_poids_disponibles"] = dispo
        r["score"] = round(brut * 100 / dispo, 1) if dispo else None
        if r["id"] == LAVAL_ID:
            r["comparable"] = "Référence (CCILaval)"
        elif r["score"] is not None and r["score"] >= 70:
            r["comparable"] = "Oui, forte"
        elif r["score"] is not None and r["score"] >= 50:
            r["comparable"] = "Oui, partielle"
        else:
            r["comparable"] = "Non"


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    return {
        "n": len(vals),
        "mediane": round(statistics.median(vals), 2),
        "moyenne": round(statistics.mean(vals), 2),
        "min": round(min(vals), 2),
        "max": round(max(vals), 2),
    }


def calculer():
    b = lire_json(BRUTES)
    denom = {str(r["code_sdr"]): r for r in b["denominateurs"]}
    struct = {str(r["code_sdr"]): r for r in b["structure_economique"]}
    res = [calculer_chambre(c, denom, struct) for c in b["chambres"]]
    comparabilite(res)
    res.sort(key=lambda r: -(r["entreprises_avec_employes"] or 0))
    for i, r in enumerate(res, 1):
        r["rang"] = i

    fiables = [r for r in res if r["confiance"] in ("élevée", "moyenne") and r["ratio_ABC"] is not None]
    comp = [r for r in res if r["comparable"] in ("Oui, forte", "Oui, partielle")]
    comp_fiables = [r for r in comp if r in fiables]
    synth = {
        "ensemble_fiable": {"ABC": stats([r["ratio_ABC"] for r in fiables]), "A": stats([r["ratio_A"] for r in fiables]),
                            "hab": stats([r["ratio_hab"] for r in fiables])},
        "comparables_fiables": {"ABC": stats([r["ratio_ABC"] for r in comp_fiables]),
                                "A": stats([r["ratio_A"] for r in comp_fiables])},
        "par_taille": {},
        "couverture": {
            "chambres_dans_etude": len(res),
            "avec_montant": sum(1 for r in res if r["total_ABC"] > 0),
            "avec_montant_fiable": len(fiables),
        },
    }
    for _, nom in SEUILS_TAILLE:
        g = [r for r in fiables if r["categorie_taille"] == nom]
        synth["par_taille"][nom] = {"ABC": stats([r["ratio_ABC"] for r in g]), "A": stats([r["ratio_A"] for r in g])}
    ecrire_json(RESULTATS, {"chambres": res, "synthese": synth})
    construire_classeur(b, res, synth)
    print(json.dumps(synth, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- classeur
def construire_classeur(b, res, synth):
    from openpyxl import Workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ent = Font(bold=True, color="FFFFFF")
    fond_ent = PatternFill("solid", fgColor="1F4E79")
    wrap = Alignment(wrap_text=True, vertical="top")

    def entete(ws, cols, largeurs=None):
        ws.append(cols)
        for i, _ in enumerate(cols, 1):
            cell = ws.cell(row=1, column=i)
            cell.font = ent
            cell.fill = fond_ent
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[get_column_letter(i)].width = (largeurs or {}).get(i, 16)
        ws.freeze_panes = "A2"
        ws.row_dimensions[1].height = 45

    # --- Dénominateurs
    wsD = wb.create_sheet("Dénominateurs")
    colsD = ["code_sdr", "nom_municipalite", "type_sdr", "code_dr", "nom_dr_ou_mrc", "entreprises_avec_employes",
             "total_emplacements", "periode_cbc", "population_2021", "superficie_km2", "population_recente",
             "annee_population_recente"]
    entete(wsD, colsD, {2: 28, 5: 24})
    for r in b["denominateurs"]:
        row = []
        for k in colsD:
            v = r.get(k, "")
            if k in ("entreprises_avec_employes", "total_emplacements", "population_2021", "population_recente"):
                v = entier(v)
            elif k == "superficie_km2":
                v = flottant(v)
            row.append(v)
        wsD.append(row)
    nD = wsD.max_row

    # --- Territoires (chambre -> municipalité), valeurs tirées de Dénominateurs par formules
    wsT = wb.create_sheet("Territoires")
    entete(wsT, ["id_chambre", "chambre", "code_sdr", "municipalité", "entreprises_avec_employes",
                 "total_emplacements", "population_2021"], {2: 40, 4: 28})
    for c in b["chambres"]:
        for s in c["codes_sdr"]:
            i = wsT.max_row + 1
            rng = lambda col: f"Dénominateurs!${col}$2:${col}${nD}"
            look = lambda col: f'=IFERROR(INDEX({rng(col)},MATCH($C{i},{rng("A")},0)),"")'
            wsT.append([c["id"], c["chambre"], s, look("B"), look("F"), look("G"), look("I")])
    nT = wsT.max_row

    # --- Détail des versements
    wsV = wb.create_sheet("Détail des versements")
    colsV = ["id_chambre", "chambre", "organisme_payeur", "categorie", "montant", "annee_ou_periode", "annee_debut",
             "annee_fin", "nb_annees_couvertes", "inclus_indicateur (1/0)", "motif_exclusion",
             "nb_annees_dans_periode_retenue", "nb_annees_observees_chambre", "contribution_moyenne_annuelle",
             "description", "source_titre", "source_url", "source_page_ou_extrait", "type_source",
             "date_consultation", "confiance", "verification_phase5", "remarques"]
    entete(wsV, colsV, {2: 34, 3: 26, 15: 40, 16: 30, 17: 40, 18: 50, 22: 30, 23: 50})
    for c in b["chambres"]:
        for v in c["versements"]:
            i = wsV.max_row + 1
            inclus = 1 if (v.get("inclus") and v.get("categorie") in CATS_INDICATEUR) else 0
            ver = v.get("verification", "")
            if isinstance(ver, dict):
                ver = f"{ver.get('statut', '')} — {ver.get('remarque', '')}".strip(" —")
            wsV.append([
                c["id"], c["chambre"], v.get("organisme_payeur"), v.get("categorie"), flottant(v.get("montant")),
                v.get("annee_ou_periode"), entier(v.get("annee_debut")), entier(v.get("annee_fin")),
                entier(v.get("nb_annees_couvertes")) or 1, inclus, v.get("motif_exclusion", ""),
                v.get("nb_annees_dans_periode_retenue", 0), v.get("nb_annees_observees_chambre", 0),
                f"=IF(AND(J{i}=1,M{i}>0),E{i}/I{i}*L{i}/M{i},0)",
                v.get("description"), v.get("source_titre"), v.get("source_url"), v.get("source_page_ou_extrait"),
                v.get("type_source"), v.get("date_consultation"), v.get("confiance"), ver, v.get("remarques"),
            ])
            for col in (15, 18, 23):
                wsV.cell(row=i, column=col).alignment = wrap
    nV = max(wsV.max_row, 2)

    # --- Synthèse
    ws = wb["Sheet"]
    ws.title = "Synthèse"
    wb.move_sheet("Synthèse", offset=-10)
    colsS = ["Rang par taille", "Catégorie de taille", "Chambre", "Municipalités desservies", "Région administrative",
             "Population", "Entreprises avec employés", "Total des emplacements",
             "Aide municipale annuelle moyenne — A", "Catégorie B", "Catégorie C", "Total A+B+C",
             "$/entreprise/année (A+B+C)", "$/entreprise/année (A seulement)", "$/habitant/année",
             "Période de référence", "Confiance globale", "Comparable à la CCILaval", "Remarques", "id"]
    entete(ws, colsS, {2: 22, 3: 40, 4: 40, 5: 22, 16: 14, 17: 13, 18: 18, 19: 60, 20: 12})
    tri = res
    Tid = f"Territoires!$A$2:$A${nT}"
    Vid, Vcat, Vcontrib = (f"'Détail des versements'!${c}$2:${c}${nV}" for c in ("A", "D", "N"))
    for r in tri:
        i = ws.max_row + 1
        c = next(x for x in b["chambres"] if x["id"] == r["id"])
        rem = []
        if r["hors_fenetre"]:
            rem.append("Montants hors 2023-2025 (dernière année disponible).")
        if not r["denominateur_complet"]:
            rem.append("Dénominateur incomplet.")
        if r["statut_collecte"]:
            rem.append(f"Statut de collecte : {r['statut_collecte']}.")
        if c.get("remarques_orchestrateur"):
            rem.append(c["remarques_orchestrateur"])
        ws.append([
            r["rang"],
            f'=IF(G{i}="","Indéterminée",IF(G{i}>=20000,"{SEUILS_TAILLE[0][1]}",IF(G{i}>=8000,"{SEUILS_TAILLE[1][1]}",'
            f'IF(G{i}>=3000,"{SEUILS_TAILLE[2][1]}",IF(G{i}>=1000,"{SEUILS_TAILLE[3][1]}","{SEUILS_TAILLE[4][1]}")))))',
            r["chambre"], "; ".join(r["municipalites_desservies"]), r["region_administrative"],
            f"=SUMIFS(Territoires!$G$2:$G${nT},{Tid},$T{i})",
            f"=SUMIFS(Territoires!$E$2:$E${nT},{Tid},$T{i})",
            f"=SUMIFS(Territoires!$F$2:$F${nT},{Tid},$T{i})",
            f'=ROUND(SUMIFS({Vcontrib},{Vid},$T{i},{Vcat},"A"),0)',
            f'=ROUND(SUMIFS({Vcontrib},{Vid},$T{i},{Vcat},"B"),0)',
            f'=ROUND(SUMIFS({Vcontrib},{Vid},$T{i},{Vcat},"C"),0)',
            f"=SUM(I{i}:K{i})",
            f'=IF(OR(L{i}=0,G{i}=0),"",ROUND(L{i}/G{i},2))',
            f'=IF(OR(L{i}=0,G{i}=0),"",ROUND(I{i}/G{i},2))',
            f'=IF(OR(L{i}=0,F{i}=0),"",ROUND(L{i}/F{i},2))',
            r["periode"], r["confiance"], r["comparable"], " ".join(rem), r["id"],
        ])
        ws.cell(row=i, column=19).alignment = wrap
        ws.cell(row=i, column=4).alignment = wrap
    nS = ws.max_row
    for col in "FGHIJKL":
        for i in range(2, nS + 1):
            ws[f"{col}{i}"].number_format = "# ##0"
    for col in "MNO":
        for i in range(2, nS + 1):
            ws[f"{col}{i}"].number_format = "0.00"
    jaune = PatternFill("solid", fgColor="FFE699")
    vert = PatternFill("solid", fgColor="C6EFCE")
    vert_pale = PatternFill("solid", fgColor="E2F0D9")
    ws.conditional_formatting.add(f"A2:T{nS}", FormulaRule(formula=[f'$T2="{LAVAL_ID}"'], fill=jaune, font=Font(bold=True)))
    ws.conditional_formatting.add(f"A2:T{nS}", FormulaRule(formula=['$R2="Oui, forte"'], fill=vert))
    ws.conditional_formatting.add(f"A2:T{nS}", FormulaRule(formula=['$R2="Oui, partielle"'], fill=vert_pale))
    ws.auto_filter.ref = f"A1:T{nS}"

    # --- Non trouvés
    wsN = wb.create_sheet("Non trouvés")
    entete(wsN, ["Chambre", "Région administrative", "Municipalités desservies", "Statut de collecte",
                 "Sources consultées sans résultat", "Remarques"], {1: 40, 3: 40, 5: 90, 6: 50})
    for c in b["chambres"]:
        r = next(x for x in res if x["id"] == c["id"])
        if r["total_ABC"] == 0:
            wsN.append([c["chambre"], c["region_administrative"], "; ".join(c["municipalites_desservies"]),
                        c["statut_collecte"], "\n".join(c["sources_consultees_sans_resultat"]),
                        c.get("remarques_orchestrateur", "")])
            wsN.cell(row=wsN.max_row, column=5).alignment = wrap
    for x in b.get("inventaire_non_couvert", []):
        wsN.append([x.get("chambre"), x.get("region_administrative"), "; ".join(x.get("municipalites_desservies", [])),
                    "non traitée", "", x.get("remarque", "")])

    # --- Comparables CCILaval
    wsC = wb.create_sheet("Comparables CCILaval")
    wsC.append(["Grille de comparabilité (poids sur 100)"])
    wsC["A1"].font = Font(bold=True, size=12)
    grille = [
        ("Entreprises avec employés", POIDS["entreprises"], "Pleins points entre 0,5 et 1,5 fois Laval; décroissance (échelle logarithmique) jusqu'à 0 à 0,25 ou 3 fois Laval."),
        ("Population", POIDS["population"], "Même règle que pour les entreprises."),
        ("Territoire", POIDS["territoire"], "Une seule municipalité (ville ou ville-MRC) = 100 %; plusieurs municipalités dont une ≥ 80 % de la population = 60 %; 50-80 % = 30 %; sinon 0."),
        ("Contexte métropolitain", POIDS["contexte"], "Banlieue de la RMR de Montréal ou ville adossée à un pôle plus grand = 100 %; banlieue d'une autre RMR = 60 %; ville centrale d'une RMR = 50 %; Montréal = 30 %; centre d'une AR = 20 %; hors RMR/AR = 0."),
        ("Structure économique", POIDS["structure"], "Part des emplacements avec employés en construction, fabrication, commerce de gros, transport et entreposage (SCIAN 23, 31-33, 41, 48-49) : pleins points si écart ≤ 3 points de %, 0 à 10 points ou plus. Critère non évalué = score ramené sur les poids disponibles."),
    ]
    wsC.append(["Critère", "Poids", "Règle"])
    for g in grille:
        wsC.append(list(g))
    wsC.append([])
    wsC.append(["Seuils : « Oui, forte » ≥ 70; « Oui, partielle » 50 à 69."])
    wsC.append([])
    h = wsC.max_row + 1
    cols = ["Rang de comparabilité", "Chambre", "Entreprises (pts)", "Population (pts)", "Territoire (pts)",
            "Contexte (pts)", "Structure (pts)", "Poids disponibles", "Score /100", "Classement",
            "$/entreprise/année (A+B+C)", "$/entreprise/année (A)", "Confiance", "id"]
    wsC.append(cols)
    for j in range(1, len(cols) + 1):
        wsC.cell(row=h, column=j).font = ent
        wsC.cell(row=h, column=j).fill = fond_ent
        wsC.cell(row=h, column=j).alignment = Alignment(wrap_text=True)
    classes = sorted([r for r in res if r["score"] is not None], key=lambda r: -r["score"])
    lav = next(r for r in res if r["id"] == LAVAL_ID)
    top = [lav] + [r for r in classes if r["id"] != LAVAL_ID][:8]
    Sid = f"Synthèse!$T$2:$T${nS}"
    debut = wsC.max_row + 1
    for k, r in enumerate(top):
        i = wsC.max_row + 1
        d = r["score_detail"]
        wsC.append([
            "Réf." if r["id"] == LAVAL_ID else k, r["chambre"], d["entreprises"], d["population"], d["territoire"],
            d["contexte"], d["structure"], r["score_poids_disponibles"],
            f"=ROUND(SUM(C{i}:G{i})*100/H{i},1)", r["comparable"],
            f'=INDEX(Synthèse!$M$2:$M${nS},MATCH($N{i},{Sid},0))',
            f'=INDEX(Synthèse!$N$2:$N${nS},MATCH($N{i},{Sid},0))',
            r["confiance"], r["id"],
        ])
    fin = wsC.max_row
    wsC.append([])
    g0 = wsC.max_row + 1
    rngC = f"K{debut + 1}:K{fin}"
    rngA = f"L{debut + 1}:L{fin}"
    wsC.append(["", "Comparables (8 premiers, données disponibles) — médiane", "", "", "", "", "", "", "", "",
                f"=IFERROR(MEDIAN({rngC}),\"\")", f"=IFERROR(MEDIAN({rngA}),\"\")"])
    wsC.append(["", "Comparables — moyenne", "", "", "", "", "", "", "", "",
                f"=IFERROR(ROUND(AVERAGE({rngC}),2),\"\")", f"=IFERROR(ROUND(AVERAGE({rngA}),2),\"\")"])
    fiab = f'Synthèse!$Q$2:$Q${nS}'
    wsC.append(["", "Ensemble des chambres (confiance élevée ou moyenne) — médiane", "", "", "", "", "", "", "", "",
                f"=ROUND(MEDIAN(IF(({fiab}=\"élevée\")+({fiab}=\"moyenne\"),IF(Synthèse!$M$2:$M${nS}<>\"\",Synthèse!$M$2:$M${nS}))),2)", ""])
    wsC.append(["", "Ensemble des chambres (confiance élevée ou moyenne) — moyenne", "", "", "", "", "", "", "", "",
                f'=ROUND(AVERAGEIFS(Synthèse!$M$2:$M${nS},{fiab},"élevée")*COUNTIFS({fiab},"élevée",Synthèse!$M$2:$M${nS},">0")/COUNTIFS({fiab},"élevée",Synthèse!$M$2:$M${nS},">0"),2)', ""])
    # Les deux dernières cellules sont recalculées proprement par le script (voir rapport) : on remplace
    # par des formules matricielles simples pour LibreOffice/Excel.
    wsC.cell(row=g0 + 2, column=11).value = None
    wsC.cell(row=g0 + 3, column=11).value = None
    st = synth["ensemble_fiable"]["ABC"]
    wsC.cell(row=g0 + 2, column=11).value = st.get("mediane")
    wsC.cell(row=g0 + 3, column=11).value = st.get("moyenne")
    wsC.cell(row=g0 + 2, column=13).value = f"valeur calculée par calculs.py (n = {st.get('n', 0)})"
    wsC.cell(row=g0 + 3, column=13).value = f"valeur calculée par calculs.py (n = {st.get('n', 0)})"
    wsC.append(["", "CCILaval", "", "", "", "", "", "", "", "",
                f'=INDEX(Synthèse!$M$2:$M${nS},MATCH("{LAVAL_ID}",{Sid},0))',
                f'=INDEX(Synthèse!$N$2:$N${nS},MATCH("{LAVAL_ID}",{Sid},0))'])
    for col, w in zip("ABCDEFGHIJKLMN", [12, 46, 12, 12, 12, 12, 12, 12, 10, 16, 16, 16, 30, 12]):
        wsC.column_dimensions[col].width = w
    for i in range(3, 3 + len(grille)):
        wsC.cell(row=i, column=3).alignment = wrap
    wsC.column_dimensions["C"].width = 12

    wb.save(XLSX)
    print(f"{XLSX.name} écrit ({len(res)} chambres)")


if __name__ == "__main__":
    etape = sys.argv[1] if len(sys.argv) > 1 else "tout"
    if etape in ("consolider", "tout"):
        consolider()
    if etape in ("calculer", "tout"):
        calculer()
