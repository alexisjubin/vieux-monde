"""Vérifie les fichiers d'événements : python outils/verifier_donnees.py [fichiers en plus]"""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding="utf-8")


def lire(chemin):
    return json.loads(Path(chemin).read_text(encoding="utf-8"))


referentiel = lire(RACINE / "donnees/referentiel.json")
eres = {e["id"]: e for e in referentiel["eres"]}
regions = {r["id"] for r in referentiel["regions"]}
factions = {f["id"] for f in referentiel["factions"]}
fiabilites = {f["id"] for f in referentiel["fiabilites"]}
lieux = {l["id"] for l in lire(RACINE / "donnees/carte.json")["lieux"]}
CHAMPS = {"id", "annee", "fin", "approx", "titre", "resume", "ere", "regions", "lieux",
          "factions", "importance", "fiabilite", "note", "sources"}
LANGUES = ("fr", "en", "de")
INTERDITS = re.compile("[\u2014\u2013;]")
erreurs = []


def trilingue(valeur, nom, ident, requis=True):
    if isinstance(valeur, str):
        if requis and nom in ("titre", "resume"):
            erreurs.append(f"{ident} : {nom} doit être trilingue")
        return
    if not isinstance(valeur, dict) or set(valeur) != set(LANGUES):
        erreurs.append(f"{ident} : {nom} doit avoir fr, en et de")
        return
    for langue in LANGUES:
        if requis and not valeur[langue].strip():
            erreurs.append(f"{ident} : {nom}.{langue} vide")
        if INTERDITS.search(valeur[langue]):
            erreurs.append(f"{ident} : {nom}.{langue} contient un tiret long ou un point-virgule")


def verifier(ev):
    ident = ev.get("id", "?")
    manque = CHAMPS - set(ev)
    if manque or set(ev) - CHAMPS:
        erreurs.append(f"{ident} : champs incorrects {sorted(manque | (set(ev) - CHAMPS))}")
        return
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", ident):
        erreurs.append(f"{ident} : identifiant mal formé")
    ere = eres.get(ev["ere"])
    if not ere:
        erreurs.append(f"{ident} : âge inconnu {ev['ere']}")
    elif not ere["debut"] - 1 <= ev["annee"] <= ere["fin"]:  # une année de marge aux bornes
        erreurs.append(f"{ident} : année {ev['annee']} hors de l'âge {ev['ere']}")
    if ev["fin"] is not None and ev["fin"] < ev["annee"]:
        erreurs.append(f"{ident} : fin avant le début")
    for nom, valeurs, connus in (("région", ev["regions"], regions), ("faction", ev["factions"], factions),
                                 ("lieu", ev["lieux"], lieux)):
        for valeur in valeurs:
            if valeur not in connus:
                erreurs.append(f"{ident} : {nom} inconnu(e) {valeur}")
    if not ev["regions"] or not ev["factions"]:
        erreurs.append(f"{ident} : régions ou factions vides")
    if ev["importance"] not in (1, 2, 3):
        erreurs.append(f"{ident} : importance {ev['importance']}")
    if ev["fiabilite"] not in fiabilites:
        erreurs.append(f"{ident} : fiabilité {ev['fiabilite']}")
    trilingue(ev["titre"], "titre", ident)
    trilingue(ev["resume"], "resume", ident)
    trilingue(ev["note"], "note", ident, requis=False)
    if not ev["sources"]:
        erreurs.append(f"{ident} : aucune source")
    for source in ev["sources"]:
        if set(source) != {"titre", "detail", "url"}:
            erreurs.append(f"{ident} : source mal formée")


fichiers = sorted(glob.glob(str(RACINE / "donnees/evenements-*.json"))) + sys.argv[1:]
tous = []
for fichier in fichiers:
    for ev in lire(fichier):
        verifier(ev)
        tous.append(ev)
for ident, n in Counter(e.get("id") for e in tous).items():
    if n > 1:
        erreurs.append(f"{ident} : identifiant présent {n} fois")
print(f"{len(tous)} événements, {len(erreurs)} erreurs")
print("\n".join(erreurs[:80]))
sys.exit(1 if erreurs else 0)
