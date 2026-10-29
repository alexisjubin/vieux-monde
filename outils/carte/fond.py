"""Peint les fonds de la carte : la mer et les terres en dégradés, façon parchemin.

Comme sur la carte d'Immortal Empires, la mer est très sombre au ras des
côtes et s'éclaircit vers le large, et les terres sont un parchemin clair
marbré de taches. Ces dégradés ne se font pas bien en SVG : ils sont peints
ici en images, d'après le masque des terres (cache/terre.png), puis posés
sous les tracés par dessiner.py. Le grain fin est ajouté à chaque tuile par
tuiles.py.

Sorties dans outils/carte/cache/ (non publiées) : fond-mer.jpg, fond-terre.jpg
et plateau.json, la ligne du plateau continental tracée au large des côtes.

    .venv/Scripts/python.exe outils/carte/fond.py
"""

import json
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

ICI = Path(__file__).resolve().parent
CACHE = ICI / "cache"

MER_COTE = (66, 44, 27)
MER_LARGE = (162, 126, 84)
TERRE = (228, 200, 148)
TERRE_CLAIRE = (238, 218, 176)
TERRE_TACHE = (192, 156, 104)
PLATEAU = 110  # distance de la ligne du plateau à la côte, en unités


def bruit(forme, sigma, alea):
    """Bruit lent (taches), de moyenne 0 et d'écart type 1."""
    b = cv2.GaussianBlur(alea.standard_normal(forme).astype(np.float32), (0, 0), sigma)
    return b / b.std()


def melange(a, b, t):
    t = t[..., None]
    return np.asarray(a, np.float32) * (1 - t) + np.asarray(b, np.float32) * t


def main(pas=2):
    terre_pleine = cv2.imread(str(CACHE / "terre.png"), cv2.IMREAD_GRAYSCALE)
    ouest = json.loads((CACHE / "cotes.json").read_text(encoding="utf-8")).get("ouest", 0)  # colonne 0 = x -ouest
    H, W = terre_pleine.shape
    terre = cv2.resize(terre_pleine, (W // pas, H // pas), interpolation=cv2.INTER_AREA) > 127
    forme = terre.shape
    vers_terre = ndimage.distance_transform_edt(~terre).astype(np.float32) * pas  # distance à la côte, en mer
    vers_mer = ndimage.distance_transform_edt(terre).astype(np.float32) * pas  # distance à la côte, sur terre
    alea = np.random.default_rng(2522)
    taches = 0.65 * bruit(forme, 130 / pas, alea) + 0.35 * bruit(forme, 35 / pas, alea)
    nuages = bruit(forme, 220 / pas, alea)

    # Mer : sombre au ras des côtes, de plus en plus claire vers le large, marbrée.
    t = np.clip(vers_terre / 280, 0, 1) ** 0.5
    mer = melange(MER_COTE, MER_LARGE, t)
    mer *= (1 + 0.07 * taches + 0.05 * nuages)[..., None]
    # Au large, de grandes plages plus sombres, comme des fonds marins.
    mer *= (1 - 0.12 * np.clip(nuages, 0, None) * t)[..., None]

    # Terres : parchemin clair, plus clair près des côtes, avec des taches brunes.
    terre_c = melange(TERRE, TERRE_CLAIRE, np.exp(-vers_mer / 45) * 0.6)
    terre_c = melange(terre_c, TERRE_TACHE, np.clip(taches * 0.4 + 0.12, 0, 0.8))
    terre_c *= (1 + 0.04 * nuages)[..., None]

    for nom, image in (("fond-mer.jpg", mer), ("fond-terre.jpg", terre_c)):
        image = cv2.resize(np.clip(image, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(str(CACHE / nom), cv2.cvtColor(image, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])

    # Ligne du plateau : là où la distance à la côte vaut PLATEAU.
    au_large = (cv2.GaussianBlur(vers_terre, (0, 0), 6 / pas) > PLATEAU).astype(np.uint8)
    contours, _ = cv2.findContours(au_large, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    traits = []
    for c in contours:
        if cv2.arcLength(c, True) < 300 / pas:
            continue
        c = cv2.approxPolyDP(c, 1.0, True)[:, 0, :] * pas - [ouest, 0]
        traits.append(np.round(c, 1).tolist())
    (CACHE / "plateau.json").write_text(json.dumps(traits), encoding="utf-8")
    print(f"fonds {W} x {H}, {len(traits)} lignes de plateau")


if __name__ == "__main__":
    main()
