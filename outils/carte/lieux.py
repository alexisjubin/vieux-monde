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

import cv2
import numpy as np
from scipy import ndimage

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
            "province": re.sub(r"\s*\(province\)$", "", province[1].strip()) if province else None,
            "x": round((x - x0) * k),
            "y": round((y1 - y) * k),
        }


def dedans(pt, poly):
    x, y = pt
    vrai = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            vrai = not vrai
    return vrai


# Noms des provinces en français et en allemand (outils/carte/provinces.json),
# l'anglais étant celui du jeu.
PROVINCES = json.loads((ICI / "provinces.json").read_text(encoding="utf-8")) if (ICI / "provinces.json").exists() else {}


def traduire(nom):
    t = PROVINCES.get(nom)
    return {"fr": t["fr"], "en": nom, "de": t["de"]} if t else nom


def province_du_jeu(nom, x, y, colonies):
    """Province de la colonie du jeu qui porte ce nom (la plus proche s'il y en a plusieurs)."""
    noms = [nom["en"], nom["fr"]] if isinstance(nom, dict) else [nom]
    cles = {cle(n) for n in noms} | {cle(n.split("(")[0]) for n in noms}
    memes = [c for c in colonies if c["province"] and cle(c["nom"]) in cles]
    if not memes:
        return None
    return min(memes, key=lambda c: (c["x"] - x) ** 2 + (c["y"] - y) ** 2)["province"]


def lisser(p, ferme, passes=3):
    """Arrondit une ligne brisée (Chaikin). Une ligne ouverte garde ses deux extrémités."""
    p = np.asarray(p, np.float64)
    for _ in range(passes):
        if len(p) < 3:
            break
        a, b = (p, np.roll(p, -1, axis=0)) if ferme else (p[:-1], p[1:])
        r = np.empty((len(a) * 2, 2))
        r[0::2] = 0.75 * a + 0.25 * b
        r[1::2] = 0.25 * a + 0.75 * b
        p = r if ferme else np.vstack([p[:1], r[1:-1], p[-1:]])
    # On retire les points superflus des courbes obtenues.
    return cv2.approxPolyDP(p.astype(np.float32).reshape(-1, 1, 2), 0.4, ferme)[:, 0, :]


def decouper_provinces(graines, pas=2, portee=240):
    """Zones des provinces : chaque point des terres revient à la colonie la plus proche.

    Calcul sur le masque des terres (cache/terre.png) réduit d'un facteur `pas`.
    Au-delà de `portee` unités de toute colonie, la terre n'appartient à
    aucune province. Renvoie les contours des zones et les frontières
    intérieures, sans les côtes, chacune tracée une seule fois.
    """
    terre = cv2.imread(str(ICI / "cache" / "terre.png"), cv2.IMREAD_GRAYSCALE)
    terre = cv2.resize(terre, (terre.shape[1] // pas, terre.shape[0] // pas), interpolation=cv2.INTER_AREA) > 127
    noms = sorted({p for _, _, p in graines})
    numero = {n: i + 1 for i, n in enumerate(noms)}
    germes = np.zeros(terre.shape, np.int32)
    for x, y, p in graines:
        germes[min(int(y / pas), terre.shape[0] - 1), min(int(x / pas), terre.shape[1] - 1)] = numero[p]
    distance, (iy, ix) = ndimage.distance_transform_edt(germes == 0, return_indices=True)
    carte = germes[iy, ix]
    carte[distance > portee / pas] = 0
    # Les frontières droites du découpage sont déformées par un bruit lent,
    # pour des tracés souples comme sur une carte dessinée à la main.
    alea = np.random.default_rng(1)
    h, w = carte.shape
    deplacements = []
    for _ in range(2):
        bruit = cv2.GaussianBlur(alea.standard_normal((h, w)).astype(np.float32), (0, 0), 70 / pas)
        deplacements.append(bruit / bruit.std() * (28 / pas))
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    carte = cv2.remap(carte.astype(np.float32), gx + deplacements[0], gy + deplacements[1], cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE).astype(np.int32)
    carte[~terre] = 0
    # Un filtre de mode adoucit les frontières en escalier.
    carte = ndimage.generic_filter(carte, lambda v: np.bincount(v.astype(np.int64)).argmax(), size=5, mode="nearest").astype(np.int32)
    carte[~terre] = 0

    def points(c):
        return [[int(round(x * pas)), int(round(y * pas))] for x, y in c]

    zones, frontieres = [], []
    voisins = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for nom in noms:
        n = numero[nom]
        masque = (carte == n).astype(np.uint8)
        contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        polygones = []
        for c in contours:
            if cv2.contourArea(c) < 20:
                continue
            polygones.append(points(lisser(cv2.approxPolyDP(c, 1.5, True)[:, 0, :], ferme=True)))
            # Morceaux du contour qui touchent une province de numéro plus grand :
            # chaque frontière n'est gardée que par une des deux provinces.
            c = c[:, 0, :]
            garde = []
            for x, y in c:
                autres = {carte[min(max(y + dy, 0), h - 1), min(max(x + dx, 0), w - 1)] for dx, dy in voisins} - {n}
                garde.append(bool(autres) and 0 not in autres and min(autres) > n)
            # Un point de plus de chaque côté, pour que les frontières se rejoignent aux carrefours.
            garde = np.array(garde)
            garde = garde | np.roll(garde, 1) | np.roll(garde, -1)
            if garde.all():
                morceaux = [c]
            else:
                debut = int(np.argmin(garde))  # on part d'un point non gardé pour ne pas couper un morceau en deux
                c, garde = np.roll(c, -debut, axis=0), np.roll(garde, -debut)
                morceaux, courant = [], []
                for pt, g in zip(c, garde):
                    if g:
                        courant.append(pt)
                    elif courant:
                        morceaux.append(np.array(courant))
                        courant = []
                if courant:
                    morceaux.append(np.array(courant))
            for m in morceaux:
                if len(m) >= 3:
                    frontieres.append(points(lisser(cv2.approxPolyDP(m.reshape(-1, 1, 2).astype(np.int32), 1.5, False)[:, 0, :], ferme=False)))
        if polygones:
            zones.append([nom, polygones])
    return zones, frontieres


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

    # Les cartes détaillées font foi sur leur emprise : leurs lieux remplacent
    # les colonies de la base qui s'y trouvent.
    fichier = ICI / "cache" / "recalages.json"
    recalages = json.loads(fichier.read_text(encoding="utf-8"))["cartes"] if fichier.exists() else {}
    par_id = {l["id"]: l for l in lieux}
    toutes = list(colonies)
    graines = []  # (x, y, province) des lieux détaillés rattachés à une province du jeu
    for nom, recalage in recalages.items():
        m = recalage["matrice"]
        emprise = recalage["emprise"]
        colonies = [c for c in colonies if not dedans((c["x"], c["y"]), emprise)]
        for nom_lieu, type_lieu, x, y, ident in CONFIG["references"][nom].get("lieux", []):
            fx = round(m[0][0] * x + m[0][1] * y + m[0][2])
            fy = round(m[1][0] * x + m[1][1] * y + m[1][2])
            province = province_du_jeu(nom_lieu, fx, fy, toutes)
            if ident and ident in par_id:
                par_id[ident]["x"], par_id[ident]["y"] = fx, fy
                if province:
                    graines.append((fx, fy, province))
            elif not ident:
                colonies.append({"nom": nom_lieu, "province": province, "x": fx, "y": fy, "type": type_lieu})

    # Une province est étiquetée au barycentre de ses colonies.
    groupes = defaultdict(list)
    for c in colonies:
        if c["province"]:
            groupes[c["province"]].append(c)
    provinces = [
        {"nom": nom, "x": round(sum(c["x"] for c in cs) / len(cs)), "y": round(sum(c["y"] for c in cs) / len(cs))}
        for nom, cs in sorted(groupes.items())
    ]

    graines += [(c["x"], c["y"], c["province"]) for c in colonies if c["province"]]
    zones, frontieres = decouper_provinces(graines)

    sortie = {
        "repere": {"largeur": CONFIG["cadre"]["largeur"], "hauteur": int(1167 * k)},
        "lieux": lieux,
        "colonies": [[c["nom"], c["x"], c["y"]] + ([c["type"]] if c.get("type") else []) for c in colonies if "lieu" not in c],
        "provinces": [[traduire(p["nom"]), p["x"], p["y"]] for p in provinces],
        "zones": [[traduire(nom), polygones] for nom, polygones in zones],
        "frontieres": frontieres,
    }
    # Grands noms (mers, continents, royaumes) : outils/carte/etiquettes.json, en pixels de la référence.
    fichier = ICI / "etiquettes.json"
    # Un nom peut aussi être placé sur une carte détaillée : "carte" et "px".
    def placer(e):
        if "carte" in e and e["carte"] in recalages:
            m = recalages[e["carte"]]["matrice"]
            x, y = e["px"]
            return round(m[0][0] * x + m[0][1] * y + m[0][2]), round(m[1][0] * x + m[1][1] * y + m[1][2])
        return round(e["ie_px"][0] * k), round(e["ie_px"][1] * k)

    if fichier.exists():
        sortie["etiquettes"] = []
        for e in json.loads(fichier.read_text(encoding="utf-8")):
            x, y = placer(e)
            sortie["etiquettes"].append({**{c: v for c, v in e.items() if c not in ("ie_px", "carte", "px")}, "x": x, "y": y})
    ancien = RACINE / "donnees" / "carte.json"
    texte = json.dumps(sortie, ensure_ascii=False, separators=(",", ":"))
    texte = texte.replace('{"id"', '\n{"id"').replace('],["', '],\n["')
    ancien.write_text(texte + "\n", encoding="utf-8")
    print(f"{len(lieux)} lieux, {len(sortie['colonies'])} autres colonies, {len(provinces)} provinces")
    if sans_position:
        print("Sans position :", ", ".join(sans_position))


if __name__ == "__main__":
    main()
