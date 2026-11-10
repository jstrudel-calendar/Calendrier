#!/usr/bin/env python3
"""Construit normalisation.json : décisions de l'orchestrateur (territoires, années, inclusion, montants
vérifiés à la source le 2026-11-10). Exécuter : python3 -I construire-normalisation.py"""
import json
from pathlib import Path

ICI = Path(__file__).resolve().parent
D = "2026-11-10"


def lire(f, nom):
    return next(d for d in json.load(open(ICI / f, encoding="utf-8")) if isinstance(d, dict) and d.get("chambre") == nom)


def v(payeur, cat, montant, periode, debut, fin, nb, desc, titre, url, extrait, conf, rem="", inclus=None, motif="",
      type_source="municipale", verif=""):
    x = {"organisme_payeur": payeur, "categorie": cat, "montant": montant, "annee_ou_periode": periode,
         "annee_debut": debut, "annee_fin": fin, "nb_annees_couvertes": nb, "description": desc,
         "source_titre": titre, "source_url": url, "source_page_ou_extrait": extrait, "type_source": type_source,
         "date_consultation": D, "confiance": conf, "remarques": rem, "motif_exclusion": motif,
         "verification": verif}
    if inclus is not None:
        x["inclus"] = inclus
    return x


chambres, ajouts = [], {}

# ---------------------------------------------------------------- CCILaval
nom = "Chambre de commerce et d'industrie de Laval (CCILaval)"
src = lire("phase4-ccilaval.json", nom)["versements"]
ann = [(2022, 2023), (2024, 2025), (2024, 2025), (2021, 2023)]
lav = []
for s, (d, f) in zip(src, ann):
    x = dict(s)
    x.update({"annee_debut": d, "annee_fin": f, "nb_annees_couvertes": f - d + 1,
              "verification": "Non revérifié au 2e passage : laval.ca refuse le téléchargement automatisé (contrôle anti-robot) et "
                              "aucune nouvelle source n'a été trouvée par recherche. Montant tiré d'extraits de documents municipaux."})
    lav.append(x)
lav[2]["verification"] = ("Phase 5 : la citation attribuée au communiqué de la CCILaval du 25 novembre 2024 (« 200 000 $ de la Ville de Laval ») "
                          "n'y figure pas; le communiqué nomme « Laval économique / Ville de Laval » sans montant. Le montant ne repose que sur l'extrait "
                          "de la résolution CM-20240604-590 (laval.ca, document non téléchargeable). À confirmer.")
lav[3]["annee_ou_periode"] = "2021-2024 (programme de 3 ans, juin 2021 à juin 2024), réparti sur 2021, 2022 et 2023"
lav[3]["verification"] = "Phase 5 : confirmé (argent municipal, catégorie B)."
lav[0]["verification"] = "Phase 5 : non vérifiable (laval.ca bloqué); catégorie B cohérente (Prox-Commerce, Évolution Laval)."
lav[1]["verification"] = "Phase 5 : non vérifiable (laval.ca bloqué); catégorie indéterminée (A possible)."
lav[3]["remarques"] = (lav[3].get("remarques", "") + " Orchestrateur : programme de 3 ans lancé en juin 2021 (juin 2021 à juin 2024); "
                       "réparti sur 2021, 2022 et 2023 (1/3 par an); seule la tranche 2023 entre dans la période.").strip()
chambres.append({"id": "ccilaval", "fichier": "phase4-ccilaval.json", "nom_source": nom,
                 "chambre": "Chambre de commerce et d'industrie de Laval (CCILaval)", "codes_sdr": ["2465005"],
                 "municipalites_desservies": ["Laval"], "region_administrative": "13 Laval",
                 "contexte": "banlieue_rmr_montreal", "annees_observees": [2023, 2024, 2025], "remplacer_versements": True,
                 "remarques_orchestrateur": "Quatre ententes avec la Ville de Laval (toutes classées B). Montants de confiance moyenne : à confirmer dans les procès-verbaux (CE-20240529, CM-20240604-589 et -590) et les états financiers de la CCILaval. Commandites, cotisation et argent provincial (MEIE) non comptés."})
ajouts["ccilaval"] = lav

# ---------------------------------------------------------------- CCIQ (Québec)
QL = "https://www.ville.quebec.qc.ca/gens_affaires/fournisseur/contrats-octroyes/docs/"
ajouts["cciq"] = [
    v("Ville de Québec", "C", 25000, "2023 (contrat du 2023-02-16)", 2023, 2023, 1,
      "Soirée Fidéides 2023 — partenaire présentateur des catégories « Événement ou attraction touristique de l'année » et « Prix industrie touristique de l'année ».",
      "Ville de Québec, liste mensuelle des contrats, février 2023", QL + "Liste%20mensuelle%20f%C3%A9vrier%202023.pdf",
      "« Soirée Fidéides 2023 - Partenaire présentateur des catégories […] » BC 3629563, 2023-02-16, 25 000,00 $", "élevée",
      "Taxes : non précisé. Fait établi (document municipal primaire, téléchargé et lu).", verif="Lu à la source par l'orchestrateur."),
    v("Ville de Québec", "C", 13500, "2023 (BC du 2023-03-27)", 2023, 2023, 1,
      "Achat de visibilité — Fidéides — PRHQ 2023 — partenaire présentateur catégorie Entreprise collective.",
      "Ville de Québec, liste des transactions de plus de 2 000 $ (cumul > 25 000 $), janvier à décembre 2023",
      QL + "liste-transactions-janvier-decembre-2023.pdf", "BC 3636421, 2023-03-27, « Achat de visibilité - Fidéides - PRHQ 2023 », 13 500,00 $", "élevée",
      "Bon de commande distinct du contrat de 25 000 $ (numéro différent); pas de double compte présumé, à valider.", verif="Lu à la source par l'orchestrateur."),
    v("Ville de Québec", "B", 33900, "2023 (contrat du 2023-06-21)", 2023, 2023, 1,
      "Services professionnels — consultation et sondage auprès des entreprises et acteurs économiques (Zone économique métropolitaine Québec-Lévis).",
      "Ville de Québec, liste mensuelle des contrats, juin 2023", QL + "Liste%20mensuelle%20juin%202023.pdf",
      "BC 3652329, 2023-06-21, dérogation 573.3 LCV (OBNL), 33 900,00 $", "élevée",
      "Contrat de services (mandat) : catégorie B. Taxes non précisées.", verif="Lu à la source par l'orchestrateur."),
    v("Ville de Québec", "C", 25000, "2025 (contrat du 2025-03-07)", 2025, 2025, 1,
      "Partenaire — Soirée des Fidéides 2025 (contrat de fourniture d'espaces médias).",
      "Ville de Québec, liste mensuelle des contrats, mars 2025", QL + "Liste%20mensuelle%20mars%202025.pdf",
      "BC 3765346, 2025-03-07, « Partenaire - Soirée des Fédéides 2025 », 25 000,00 $", "élevée",
      "N'apparaît pas dans la liste annuelle 2025 des transactions (écart à valider : engagement vs paiement).", verif="Lu à la source par l'orchestrateur."),
    v("Ville de Québec", "B", 15000, "2025 (BC du 2025-08-20)", 2025, 2025, 1,
      "Participation à l'Indice de performance socio-économique de la CCIQ.",
      "Ville de Québec, liste des transactions janvier à décembre 2025", QL + "Liste%20des%20transactions%20de%20janvier%20%C3%A0%20d%C3%A9cembre%202025.pdf",
      "BC 3794366, 2025-08-20, « Participation à l'Indice de Performance Socio-économique », 15 000,00 $", "élevée", verif="Lu à la source par l'orchestrateur."),
    v("Ville de Québec", "C", 2151.30, "2025", 2025, 2025, 1, "Billets (événement de la CCIQ).",
      "Ville de Québec, liste des transactions janvier à décembre 2025", QL + "Liste%20des%20transactions%20de%20janvier%20%C3%A0%20d%C3%A9cembre%202025.pdf",
      "Carte d'achat, 2025-05-22, « BILLETS », 2 151,30 $", "élevée", verif="Lu à la source par l'orchestrateur."),
    v("Ville de Québec", "D", 2371.93, "2025", 2025, 2025, 1, "Cotisation de membre 2025.",
      "Ville de Québec, liste des transactions janvier à décembre 2025", QL + "Liste%20des%20transactions%20de%20janvier%20%C3%A0%20d%C3%A9cembre%202025.pdf",
      "INV-005727, « cotisation renouvellement du 01-01-2025 au 31-12-2025 », 2 371,93 $", "élevée",
      "Catégorie D : exclue de l'indicateur.", verif="Lu à la source par l'orchestrateur."),
]
chambres.append({"id": "cciq", "fichier": "phase3-quebec-cciq.json", "nom_source": "Chambre de commerce et d'industrie de Québec (CCIQ)",
                 "codes_sdr": ["2423027", "2423057", "2423072"], "municipalites_desservies": ["Québec", "L'Ancienne-Lorette", "Saint-Augustin-de-Desmaures"],
                 "region_administrative": "03 Capitale-Nationale", "contexte": "centre_rmr", "annees_observees": [2023, 2024, 2025],
                 "remplacer_versements": True,
                 "remarques_orchestrateur": "Aucune ligne CCIQ dans la liste annuelle 2024 ni dans les 12 listes mensuelles 2024 (consultées) : 2024 = 0 au-dessus des seuils de publication. Les paiements sous les seuils (moins de 25 000 $ cumulés) ne sont pas visibles : le montant est un plancher. Territoire supposé : agglomération de Québec."})

# ---------------------------------------------------------------- CCG (Gatineau)
GU = "https://www.gatineau.ca/docs/guichet_municipal/subventions_commandites/fonds_soutien_projets_contribuant_developpement_economique/"
gat_rem = "Fonds de soutien aux projets contribuant au développement économique (Ville de Gatineau). Origine des crédits (budget municipal ou fonds provincial) à confirmer."
ajouts["ccg"] = [
    v("Ville de Gatineau", "B", 80000, "2023", 2023, 2023, 1, "Projet « Virage numérique pour la gestion des ressources humaines et la rareté de la main-d'œuvre ».",
      "Ville de Gatineau, Tableau sommaire des projets retenus 2023", GU + "projets_2023.fr-CA.pdf", "Chambre de commerce de Gatineau (CCG) […] 80 000 $", "élevée", gat_rem, verif="Lu à la source par l'orchestrateur."),
    v("Ville de Gatineau", "B", 70000, "2024", 2024, 2024, 1, "Projet « Connexions innovantes » (événement d'une journée).",
      "Ville de Gatineau, Tableau sommaire des projets retenus 2024", GU + "projets_2024.fr-CA.pdf", "Connexions innovantes — Chambre de commerce de Gatineau (CCG) — 70 000 $", "élevée", gat_rem, verif="Lu à la source par l'orchestrateur."),
    v("Ville de Gatineau", "B", 40000, "2025", 2025, 2025, 1, "Projet « Soutien en exportation et au commerce interprovincial » (Rendez-vous de l'exportation).",
      "Ville de Gatineau, Tableau sommaire des projets retenus 2025", GU + "projets_2025.fr-CA.pdf", "Soutien en exportation et au commerce interprovincial — Chambre de commerce de Gatineau (CCG) — 40 000 $", "élevée",
      gat_rem + " Corrige le 45 000 $ du 1er passage.", verif="Lu à la source par l'orchestrateur (1er passage : 45 000 $, faible)."),
    v("ID Gatineau (Fonds régions et ruralité)", "B", 50000, "2024", 2024, 2024, 1, "Programme de mentorat pour entrepreneurs (45 000 $ versés au 31 décembre 2024).",
      "Ville de Gatineau, Rapport d'activité du Fonds régions et ruralité 2024",
      "https://www.gatineau.ca/docs/guichet_municipal/affaires_developpement_economique/rapport_activite_fonds_regions_ruralite_2024.fr-CA.pdf",
      "« Un montant de 50 000 $ a été octroyé par ID Gatineau à la Chambre de commerce de Gatineau (CCG) afin d'offrir […] le programme de mentorat »", "élevée",
      "Argent provincial (FRR) géré par l'organisme municipal : exclu selon les règles.", inclus=False, motif="Fonds régions et ruralité (provincial)", verif="Lu à la source par l'orchestrateur."),
]
chambres.append({"id": "ccg", "fichier": "phase3-gatineau.json", "nom_source": "Chambre de commerce de Gatineau (CCG)",
                 "codes_sdr": ["2481017"], "municipalites_desservies": ["Gatineau"], "region_administrative": "07 Outaouais",
                 "contexte": "voisine_pole_plus_grand", "annees_observees": [2023, 2024, 2025], "remplacer_versements": True,
                 "remarques_orchestrateur": "Seul le fonds municipal de projets a été lu; commandites (Gala Excelor), cotisation et procès-verbaux non consultés : plancher."})

# ---------------------------------------------------------------- CCISF (Saguenay)
ajouts["ccisf"] = [
    v("Ville de Saguenay (comité exécutif)", "A", 25000, "2025", 2025, 2025, 1, "Partenariat annuel 2025 (résolution VS-CE-2024-110).",
      "Ville de Saguenay, liste des contrats de 2 000 $ et plus totalisant 25 000 $, cumul au 31 décembre 2025",
      "https://ville.saguenay.ca/files/medias/La-ville-et-vie-d%C3%A9mocratique/Approvisionnement/Liste-des-contrats-sup%C3%A9rieurs-%C3%A0-2000-totalisant-25000-d%C3%A9cembre-2025.pdf",
      "CHAMBRE DE COMMERCE ET D'INDUSTRIE SAGUENAY-LE-FJORD — PARTENARIAT ANNUEL 2025 - VS-CE-2024-110 — 25000,00", "élevée",
      "Aucune ligne CCISF dans la liste 2024 de la Ville (consultée). Liste 2023 de la Ville non consultée.", verif="Lu à la source par l'orchestrateur."),
    v("MRC du Fjord-du-Saguenay", "A", 43730, "2025", 2025, 2025, 1, "Partenariat.",
      "MRC du Fjord-du-Saguenay, dépenses de plus de 2 000 $ totalisant plus de 25 000 $ par fournisseur, année 2025 (montants avec taxes)",
      "https://mrc-fjord.qc.ca/app/uploads/2025/05/Liste-contrat-2k-a-25k_Corrige_VF.pdf",
      "« Chambre de commerce et d'industrie Saguenay-Le Fjord — Partenariat — 43 730 $ »", "élevée",
      "Taxes incluses selon l'en-tête. Origine des crédits de la MRC (quote-parts ou FRR) non vérifiée.", verif="Lu à la source par l'orchestrateur."),
    v("MRC du Fjord-du-Saguenay", "A", 27300, "2023", 2023, 2023, 1, "Entente partenariat.",
      "MRC du Fjord-du-Saguenay, dépenses de plus de 2 000 $ totalisant plus de 25 000 $ par fournisseur, année 2023",
      "https://mrc-fjord.qc.ca/app/uploads/2023/02/Liste-contrat-2-a-25k-2023_VF.pdf",
      "« Chambre de commerce et d'industrie Saguenay-Le Fjord — Entente partenariat — 27 300 $ »", "élevée",
      "Hors des années retenues pour le calcul (2025 seule a les deux payeurs documentés); noté pour la tendance.", verif="Lu à la source par l'orchestrateur."),
]
chambres.append({"id": "ccisf", "fichier": "phase3-saguenay.json", "nom_source": "Chambre de commerce et d'industrie Saguenay-Le Fjord (CCISF)",
                 "codes_sdr": ["2494068", "2494205", "2494210", "2494220", "2494225", "2494230", "2494235", "2494240", "2494245",
                               "2494250", "2494255", "2494260", "2494265"],
                 "municipalites_desservies": ["Saguenay", "municipalités de la MRC du Fjord-du-Saguenay"], "region_administrative": "02 Saguenay–Lac-Saint-Jean",
                 "contexte": "centre_rmr", "annees_observees": [2025], "remplacer_versements": True,
                 "remarques_orchestrateur": "Période retenue : 2025 seulement (seule année où les listes des deux payeurs ont été lues). Territoire : Ville de Saguenay + MRC du Fjord-du-Saguenay (SDR non publiées par StatCan exclues)."})

# ---------------------------------------------------------------- CCIM (Les Moulins)
MRC = "https://www.mrclesmoulins.ca/wp-content/uploads/"
ajouts["ccim"] = [
    v("MRC Les Moulins", "A", 113300, "2023", 2023, 2023, 1, "Entente de partenariat 2022-2023, deux versements 2023 de 56 650 $ (50 % chacun).",
      "MRC Les Moulins, procès-verbal du 14 février 2023", MRC + "2023/04/20230214PV.pdf",
      "« QUE la dépense au montant de 113 300,00 $, soit prélevée à partir du poste budgétaire 2622-976 « Chambre de commerce et d'industrie Les Moulins » »", "élevée",
      "Poste budgétaire de la MRC (financé par les quote-parts de Terrebonne et Mascouche), pas un fonds provincial nommé.", verif="Lu à la source par l'orchestrateur."),
    v("MRC Les Moulins", "B", 12500, "2023", 2023, 2023, 1, "Addenda no 1 — volet cellule industrielle.",
      "MRC Les Moulins, procès-verbal du 14 février 2023 (résolution 14 319-02-23)", MRC + "2023/04/20230214PV.pdf",
      "« la MRC Les Moulins versera une cotisation financière supplémentaire en 2023 […] dont 12 500,00$ pour le volet portant sur la cellule industrielle »", "moyenne",
      "Autorisation de signature de l'addenda; paiement non vu.", verif="Lu à la source par l'orchestrateur."),
    v("MRC Les Moulins", "A", 64000, "2024", 2024, 2024, 1, "Paiement en lien avec l'entente de partenariat 2024-2026 (montant maximum).",
      "MRC Les Moulins, procès-verbal du 10 décembre 2024 (résolution 15 134-12-24)", "https://mrclesmoulins.ca/wp-content/uploads/2025/02/20241210PV.pdf",
      "« autorise le paiement d'un montant maximum de 64 000,00$ en lien avec l'entente de partenariat 2024-2026 »", "élevée",
      "Montant maximum autorisé; imputé à 2024. L'entente 2024-2026 a été retirée de l'ordre du jour du 29 janvier 2025 : montants 2025-2026 inconnus.", verif="Lu à la source par l'orchestrateur."),
    v("MRC Les Moulins", "C", 1520, "2025", 2025, 2025, 1, "Deux tables, Dîner du maire de Terrebonne (29 avril 2025), 760 $ par table, taxes en sus.",
      "MRC Les Moulins, procès-verbal du 8 avril 2025 (résolution 15 249-04-25)", MRC + "2025/06/20250408PV.pdf", "« l'achat de deux tables […] 760,00$ par table, excluant les taxes »", "élevée",
      "Hors des années retenues (2023-2024).", verif="Lu à la source par l'orchestrateur."),
    v("MRC Les Moulins", "C", 1520, "2025", 2025, 2025, 1, "Deux tables, Dîner du maire de Mascouche (2025), 760 $ par table, taxes en sus.",
      "MRC Les Moulins, procès-verbal du 8 avril 2025", MRC + "2025/06/20250408PV.pdf", "« certificat […] au montant de 1 520,00$, excluant les taxes »", "élevée",
      "Hors des années retenues (2023-2024).", verif="Lu à la source par l'orchestrateur."),
    v("MRC Les Moulins", "C", 1439, "2025", 2025, 2025, 1, "Tournoi des maires de la CCIM (quatre soupers).",
      "MRC Les Moulins, procès-verbal du 8 avril 2025 (résolution 15 247-04-25)", MRC + "2025/06/20250408PV.pdf", "« montant de 1 439,00$, excluant les taxes »", "élevée",
      "Hors des années retenues (2023-2024).", verif="Lu à la source par l'orchestrateur."),
]
chambres.append({"id": "ccim", "fichier": "phase3-terrebonne.json", "nom_source": "Chambre de commerce et d'industrie Les Moulins (CCIM)",
                 "codes_sdr": ["2464008", "2464015"], "municipalites_desservies": ["Terrebonne", "Mascouche"], "region_administrative": "14 Lanaudière",
                 "contexte": "banlieue_rmr_montreal", "annees_observees": [2023, 2024], "remplacer_versements": True,
                 "remarques_orchestrateur": "Période retenue : 2023-2024 (contribution de base connue). Payeur principal : la MRC Les Moulins plutôt que les villes. Versements directs des villes non repérés."})

# ---------------------------------------------------------------- CCI3R (Trois-Rivières)
nom = "Chambre de commerce et d'industries de Trois-Rivières (CCI3R)"
x = dict(lire("phase3-trois-rivieres.json", nom)["versements"][0])
x.update({"annee_debut": 2024, "annee_fin": 2028, "nb_annees_couvertes": 5,
          "verification": "Non revérifié : le site de la Ville (maruche.ca) bloque le téléchargement automatisé. Le rapport annuel 2024-2025 de la CCI3R ne publie pas le montant."})
x["remarques"] = x.get("remarques", "") + " Orchestrateur : réparti sur 5 ans (2024 à 2028), taxes incluses (42 500 $ avant taxes)."
ajouts["cci3r"] = [x]
chambres.append({"id": "cci3r", "fichier": "phase3-trois-rivieres.json", "nom_source": nom, "codes_sdr": ["2437067"],
                 "municipalites_desservies": ["Trois-Rivières"], "region_administrative": "04 Mauricie", "contexte": "centre_rmr",
                 "remplacer_versements": True,
                 "remarques_orchestrateur": "Un seul montant (entente de visibilité 2024-2029). Cotisation et autres versements non publiés : plancher."})

# ---------------------------------------------------------------- CCMM (Montréal)
nom = "Chambre de commerce du Montréal métropolitain (CCMM)"
x = dict(lire("phase3-montreal-ccmm.json", nom)["versements"][0])
x.update({"annee_debut": 2025, "annee_fin": 2025, "nb_annees_couvertes": 1, "confiance": "faible",
          "verification": "Non revérifié. Projet tripartite (CCMM, CC de l'Est de Montréal, Excellence industrielle Saint-Laurent) : part de la CCMM inconnue; année présumée."})
ajouts["ccmm"] = [x]
chambres.append({"id": "ccmm", "fichier": "phase3-montreal-ccmm.json", "nom_source": nom,
                 "codes_sdr": ["2466007", "2466023", "2466032", "2466047", "2466058", "2466062", "2466072", "2466087", "2466097",
                               "2466102", "2466107", "2466112", "2466117", "2466127", "2466142"],
                 "municipalites_desservies": ["Agglomération de Montréal (15 municipalités publiées)"], "region_administrative": "06 Montréal",
                 "contexte": "metropole", "remplacer_versements": True,
                 "remarques_orchestrateur": "Montant faible confiance (projet partagé entre trois organismes). Registres de Montréal non dépouillés. Territoire supposé : agglomération de Montréal."})

# ---------------------------------------------------------------- comparables sans montant
for cid, f, n, sdr, mun, reg, ctx, rem in [
    ("ccirs", "phase3-longueuil.json", "Chambre de commerce et d'industrie de la Rive-Sud (CCIRS)",
     ["2458227", "2458007", "2458033", "2458037", "2458012", "2459010", "2459015", "2459020", "2459025", "2459030", "2459035"],
     ["Longueuil", "Brossard", "Boucherville", "Saint-Bruno-de-Montarville", "Saint-Lambert", "Sainte-Julie", "Saint-Amable", "Varennes", "Verchères", "Calixa-Lavallée", "Contrecœur"],
     "16 Montérégie", "banlieue_rmr_montreal",
     "Rapports d'activités 2022-2023, 2023-2024 et 2024-2025 lus : DEL, Ville de Brossard, Ville de Contrecœur et RTL nommés comme partenaires, sans montant. Listes de contrats de Longueuil non dépouillées."),
    ("ccigl", "phase3-levis.json", "Chambre de commerce et d'industrie du Grand Lévis (CCIGL) — anciennement Chambre de commerce de Lévis (CCL)",
     ["2425213"], ["Lévis"], "12 Chaudière-Appalaches", "voisine_pole_plus_grand",
     "Ville de Lévis partenaire des Pléiades (2024, 2025) sans montant publié."),
    ("ccis", "phase3-sherbrooke.json", "Chambre de commerce et d'industrie de Sherbrooke (CCIS)", ["2443027"], ["Sherbrooke"], "05 Estrie",
     "centre_rmr", "Aucun versement repéré; documents municipaux non dépouillés."),
]:
    chambres.append({"id": cid, "fichier": f, "nom_source": n, "chambre": n.split(" — ")[0], "codes_sdr": sdr,
                     "municipalites_desservies": mun, "region_administrative": reg, "contexte": ctx, "remarques_orchestrateur": rem})

meta = {"date": D, "fenetre": "2023-2025", "denominateur": "StatCan 33-10-1097-01, décembre 2025",
        "population": "Recensement 2021, 98-10-0002-01"}
json.dump({"meta": meta, "chambres": chambres, "versements": {}, "ajouts": ajouts},
          open(ICI / "normalisation.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(chambres), "chambres")
