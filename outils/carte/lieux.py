"""Produit donnees/carte.json : lieux de la chronologie, colonies et provinces, dans le repère de carte.svg.

- Lieux de la chronologie : outils/carte/lieux.json. Leur position vient de
  la colonie de même nom (ou du nom donné dans `ie`), sinon de `ie_px`,
  relevé à la main en pixels de references/ie-monde.webp.
- Colonies et provinces : la carte interactive Immortal Empires
  (references/ie-factions.json). Les noms y sont en anglais, comme en jeu.

    .venv/Scripts/python.exe outils/carte/lieux.py
"""

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent.parent
CONFIG = json.loads((ICI / "references.json").read_text(encoding="utf-8"))
LARGEUR_REF = 1500


def cle(nom):
    nom = unicodedata.normalize("NFD", nom).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", nom)


def marqueurs():
    ref = CONFIG["references"][CONFIG["cadre"]["base"]]
    page = json.loads((RACINE / ref["colonies"]).read_text(encoding="utf-8"))
    contenu = json.loads(next(iter(page["query"]["pages"].values()))["revisions"][0]["slots"]["main"]["*"])
    (x0, y0), (x1, y1) = contenu["mapBounds"]
    largeur = CONFIG["cadre"]["largeur"]
    k = largeur / (x1 - x0)
    for m in contenu["markers"]:
        x, y = m["position"]
        province = re.search(r"Part of the \[\[([^\]|]+)", m["popup"].get("description", ""))
        yield {
            "nom": m["popup"]["title"].strip(),
            "province": province[1].strip() if province else None,
            "x": round((x - x0) * k),
            "y": round((y1 - y) * k),
        }


def main():
    k = CONFIG["cadre"]["largeur"] / LARGEUR_REF
    colonies = list(marqueurs())
    par_nom = {}
    for c in colonies:
        par_nom.setdefault(cle(c["nom"]), c)

    lieux, sans_position = [], []
    for l in json.loads((ICI / "lieux.json").read_text(encoding="utf-8")):
        noms = [l.get("ie"), l["nom"]["en"], l["nom"]["en"].split("(")[0], l["nom"]["fr"], l["id"].replace("-", " ")]
        trouve = next((par_nom[cle(n)] for n in noms if n and cle(n) in par_nom), None)
        sortie = {"id": l["id"], "type": l["type"], "nom": l["nom"]}
        if "ie_px" in l:
            sortie["x"], sortie["y"] = round(l["ie_px"][0] * k), round(l["ie_px"][1] * k)
        elif trouve:
            sortie["x"], sortie["y"] = trouve["x"], trouve["y"]
            trouve["lieu"] = l["id"]
        else:
            sans_position.append(l["id"])
        lieux.append(sortie)

    # Une province est étiquetée au barycentre de ses colonies.
    groupes = defaultdict(list)
    for c in colonies:
        if c["province"]:
            groupes[c["province"]].append(c)
    provinces = [
        {"nom": nom, "x": round(sum(c["x"] for c in cs) / len(cs)), "y": round(sum(c["y"] for c in cs) / len(cs))}
        for nom, cs in sorted(groupes.items())
    ]

    sortie = {
        "repere": {"largeur": CONFIG["cadre"]["largeur"], "hauteur": int(1167 * k)},
        "lieux": lieux,
        "colonies": [[c["nom"], c["x"], c["y"]] for c in colonies if "lieu" not in c],
        "provinces": [[p["nom"], p["x"], p["y"]] for p in provinces],
    }
    # Grands noms (mers, continents, royaumes) : outils/carte/etiquettes.json, en pixels de la référence.
    fichier = ICI / "etiquettes.json"
    if fichier.exists():
        sortie["etiquettes"] = [
            {**{c: v for c, v in e.items() if c != "ie_px"}, "x": round(e["ie_px"][0] * k), "y": round(e["ie_px"][1] * k)}
            for e in json.loads(fichier.read_text(encoding="utf-8"))
        ]
    ancien = RACINE / "donnees" / "carte.json"
    texte = json.dumps(sortie, ensure_ascii=False, separators=(",", ":"))
    texte = texte.replace('{"id"', '\n{"id"').replace('],["', '],\n["')
    ancien.write_text(texte + "\n", encoding="utf-8")
    print(f"{len(lieux)} lieux, {len(sortie['colonies'])} autres colonies, {len(provinces)} provinces")
    if sans_position:
        print("Sans position :", ", ".join(sans_position))


if __name__ == "__main__":
    main()
