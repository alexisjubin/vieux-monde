"""Extrait le trait de côte de la carte de référence et le vectorise.

La carte de base (references.json, clé cadre.base) est découpée en terre et
mer par ligne de partage des eaux : les graines de mer sont posées à la main,
les graines de terre sont les colonies de la carte interactive (toutes sur la
terre ferme). Le masque obtenu est agrandi au repère final (cadre.largeur
pixels de large, celui des coordonnées des colonies) par un champ de distance
signée lissé, puis converti en contours simplifiés.

    .venv/Scripts/python.exe outils/carte/construire.py

Sortie : outils/carte/cache/cotes.json, lu par dessiner.py. Les cartes de
référence (dossier references/) ne sont pas publiées.
"""

import json
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent.parent
CACHE = ICI / "cache"
CACHE.mkdir(exist_ok=True)
CONFIG = json.loads((ICI / "references.json").read_text(encoding="utf-8"))


def colonies(ref, largeur, hauteur):
    """Positions des colonies de la carte interactive, en pixels de l'image de référence."""
    page = json.loads((RACINE / ref["colonies"]).read_text(encoding="utf-8"))
    contenu = json.loads(next(iter(page["query"]["pages"].values()))["revisions"][0]["slots"]["main"]["*"])
    (x0, y0), (x1, y1) = contenu["mapBounds"]
    for m in contenu["markers"]:
        x, y = m["position"]
        yield m, (x - x0) / (x1 - x0) * largeur, (1 - (y - y0) / (y1 - y0)) * hauteur


def masque_terre(ref):
    im = cv2.imread(str(RACINE / ref["fichier"]))
    if im is None:
        raise SystemExit(f"Carte de référence introuvable : {ref['fichier']}")
    h, w = im.shape[:2]
    lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 1.5), cv2.COLOR_BGR2LAB)
    marques = np.zeros((h, w), np.int32)
    for x, y in ref["graines_mer"]:
        cv2.circle(marques, (x, y), 5, 1, -1)
    for _, x, y in colonies(ref, w, h):
        cv2.circle(marques, (int(x), int(y)), 2, 2, -1)
    for x, y in ref.get("graines_terre", []):
        cv2.circle(marques, (x, y), 4, 2, -1)
    zones = cv2.watershed(lab, marques)
    terre = (zones != 1).astype(np.uint8)
    # La ligne de partage elle-même (valeur -1) revient à la terre, ce qui
    # suit le trait de côte sombre de la carte.
    terre = cv2.morphologyEx(terre, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return terre


def nettoyer(terre, aire_min):
    """Retire les îlots et les trous plus petits que aire_min pixels (bruit d'écriture, étiquettes)."""
    for valeur in (1, 0):
        n, etiquettes, stats, _ = cv2.connectedComponentsWithStats((terre == valeur).astype(np.uint8), connectivity=4)
        petits = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] < aire_min]
        terre[np.isin(etiquettes, petits)] = 1 - valeur
    return terre


def chaikin(p, passes=2):
    """Coupe les angles (Chaikin) pour un trait plus souple, sans déplacer la côte."""
    p = np.asarray(p, np.float64)
    for _ in range(passes):
        q = np.roll(p, -1, axis=0)
        r = np.empty((len(p) * 2, 2))
        r[0::2] = 0.75 * p + 0.25 * q
        r[1::2] = 0.25 * p + 0.75 * q
        p = r
    return p


def main():
    cadre = CONFIG["cadre"]
    ref = CONFIG["references"][cadre["base"]]
    terre = masque_terre(ref)
    h, w = terre.shape
    terre = nettoyer(terre, 6)
    cv2.imwrite(str(CACHE / "masque-base.png"), terre * 255)

    k = cadre["largeur"] / w
    W, H = cadre["largeur"], int(h * k)
    champ = (ndimage.distance_transform_edt(terre) - ndimage.distance_transform_edt(1 - terre)).astype(np.float32)
    champ = cv2.resize(champ, (W, H), interpolation=cv2.INTER_CUBIC)
    champ = cv2.GaussianBlur(champ, (0, 0), k * 0.8)
    grand = (champ > 0).astype(np.uint8)
    cv2.imwrite(str(CACHE / "terre.png"), grand * 255)

    # Les terres coupées par le bord de l'image sont prolongées au-delà du cadre :
    # le lissage arrondit alors des coins invisibles, pas ceux de la carte.
    marge = 300
    grand = cv2.copyMakeBorder(grand, marge, marge, marge, marge, cv2.BORDER_REPLICATE)
    contours, hierarchie = cv2.findContours(grand, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    anneaux = []
    for c, (_, _, _, parent) in zip(contours, hierarchie[0]):
        if cv2.contourArea(c) < (k * 3) ** 2:
            continue
        simple = cv2.approxPolyDP(c, 1.2, True)[:, 0, :]
        if len(simple) < 4:
            continue
        lisse = chaikin(simple, 2) - marge
        anneaux.append({"trou": bool(parent != -1), "points": np.round(lisse, 1).tolist()})
    (CACHE / "cotes.json").write_text(json.dumps({"largeur": W, "hauteur": H, "anneaux": anneaux}), encoding="utf-8")
    print(f"Repère {W} x {H}, {len(anneaux)} contours, {sum(len(a['points']) for a in anneaux)} points")


if __name__ == "__main__":
    main()
