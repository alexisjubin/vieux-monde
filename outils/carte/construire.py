"""Extrait le trait de côte de la carte de référence et le vectorise.

La carte de base (references.json, clé cadre.base) est découpée en terre et
mer par ligne de partage des eaux : les graines de mer sont posées à la main,
les graines de terre sont les colonies de la carte interactive (toutes sur la
terre ferme). Le masque obtenu est agrandi au repère final (cadre.largeur
pixels de large, celui des coordonnées des colonies) par un champ de distance
signée lissé, puis converti en contours simplifiés.

    .venv/Scripts/python.exe outils/carte/construire.py

Les cartes détaillées (références avec `points`) remplacent la base sur
leur emprise : elles sont posées par une similitude (échelle, rotation,
translation), calée d'abord sur des points communs puis affinée en
superposant les côtes, et fondues dans la base par champs de distance
signée. Leurs proportions restent donc intactes.

Sorties dans outils/carte/cache/ : cotes.json (lu par dessiner.py) et
recalages.json (matrices et emprises, lu par lieux.py et dessiner.py). Les cartes de
référence (dossier references/) ne sont pas publiées.
"""

import json
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage
from scipy.optimize import minimize

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


def masque_teinte(ref):
    """Carte où la mer est bleutée et la terre ocre : la composante b* (jaune-bleu) les sépare.

    Les zones sûres servent de graines à une ligne de partage des eaux. Les
    décors dessinés sur la mer (cartouches, navires, monstres) sont forcés en mer.
    """
    im = cv2.imread(str(RACINE / ref["fichier"]))
    if im is None:
        raise SystemExit(f"Carte de référence introuvable : {ref['fichier']}")
    h, w = im.shape[:2]
    lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 2), cv2.COLOR_BGR2LAB)
    gris = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    moy = cv2.blur(gris, (9, 9))
    ecart = np.sqrt(np.maximum(cv2.blur(gris * gris, (9, 9)) - moy * moy, 0))
    b = cv2.GaussianBlur(lab[..., 2].astype(np.float32), (0, 0), 4)
    noyau = np.ones((9, 9), np.uint8)
    marques = np.zeros((h, w), np.int32)
    marques[cv2.erode(((b < ref["seuil_mer"]) & (ecart < 7)).astype(np.uint8), noyau) > 0] = 1
    marques[cv2.erode((b > ref["seuil_terre"]).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0] = 2
    for x, y in ref.get("graines_terre", []):
        cv2.circle(marques, (x, y), 6, 2, -1)
    for x0, y0, x1, y1 in ref.get("decors", []):
        marques[y0:y1, x0:x1] = 1
    # Cartouches clairs posés sur la terre (noms de villes) : forcés en terre.
    for x0, y0, x1, y1 in ref.get("cartouches", []):
        marques[y0:y1, x0:x1] = 2
    # Cartouches à cheval sur la côte : sans graine, la terre et la mer qui
    # les entourent se les partagent.
    for x0, y0, x1, y1 in ref.get("neutres", []):
        marques[y0:y1, x0:x1] = 0
    zones = cv2.watershed(lab, marques)
    return (zones == 2).astype(np.uint8)


def massifs_teinte(ref, terre):
    """Montagnes dessinées en blanc grisé sur la terre : clair, peu jaune et très texturé."""
    im = cv2.imread(str(RACINE / ref["fichier"]))
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    gris = lab[..., 0]
    moy = cv2.blur(gris, (11, 11))
    ecart = np.sqrt(np.maximum(cv2.blur(gris * gris, (11, 11)) - moy * moy, 0))
    b = cv2.GaussianBlur(lab[..., 2], (0, 0), 3)
    montagne = ((ecart > ref["massifs"]["texture"]) & (b < ref["massifs"]["b_max"])).astype(np.float32)
    montagne = cv2.GaussianBlur(montagne, (0, 0), 6) > 0.45
    montagne &= cv2.erode(terre, np.ones((9, 9), np.uint8)) > 0
    montagne = cv2.morphologyEx(montagne.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    return nettoyer(montagne, ref["massifs"].get("aire_min", 600))


METHODES = {"teinte": masque_teinte}


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


def similitude(points):
    """Similitude au sens des moindres carrés, de la référence vers le repère final."""
    p = np.array(points, np.float64)
    src, dst = p[:, :2], p[:, 2:]
    ms, md = src.mean(0), dst.mean(0)
    a, b = src - ms, dst - md
    u, s, vt = np.linalg.svd(b.T @ a)
    d = np.sign(np.linalg.det(u @ vt))
    r = u @ np.diag([1, d]) @ vt
    echelle = (s * [1, d]).sum() / (a ** 2).sum()
    return np.hstack([echelle * r, (md - echelle * r @ ms)[:, None]])


def affiner(m, masque, emprise, base, k):
    """Ajuste la similitude pour que les terres de la carte détaillée recouvrent au mieux celles de la base."""
    h, w = base.shape
    flou_base = cv2.GaussianBlur(base.astype(np.float32), (0, 0), 3)
    echelle0 = np.hypot(*m[:, 0])
    flou_det = cv2.GaussianBlur(masque.astype(np.float32), (0, 0), 3 * k / echelle0)
    angle0 = np.arctan2(m[1, 0], m[0, 0])

    def matrice(p):
        e, a, tx, ty = p
        c, s = np.cos(a) * e, np.sin(a) * e
        return np.array([[c, -s, tx], [s, c, ty]], np.float32)

    def ecart(p):
        mm = matrice(p) / k
        pose = cv2.warpAffine(flou_det, mm, (w, h))
        dedans = cv2.warpAffine(emprise.astype(np.float32), mm, (w, h)) > 0.99
        return float(((pose - flou_base)[dedans] ** 2).mean())

    p0 = [echelle0, angle0, m[0, 2], m[1, 2]]
    pas = [echelle0 * 0.03, 0.03, 40, 40]
    res = minimize(ecart, p0, method="Nelder-Mead",
                   options={"initial_simplex": [p0] + [[v + (d if i == j else 0) for j, (v, d) in enumerate(zip(p0, pas))] for i in range(4)],
                            "maxiter": 600, "xatol": 1e-4, "fatol": 1e-7})
    print(f"  calage affiné : écart {ecart(p0):.4f} -> {res.fun:.4f}")
    return matrice(res.x).astype(np.float64)


def poser_details(champ, base, k, W, H, ouest):
    """Fond chaque carte détaillée dans le champ de distance de la base.

    Le champ couvre aussi la bande ajoutée à l'ouest du cadre : la colonne 0
    du champ correspond à x = -ouest dans le repère de la carte.
    """
    recalages, massifs = {}, []
    decale = np.array([[0, 0, ouest], [0, 0, 0]], np.float64)
    effaces = []
    # Terres de la base à effacer : la place qu'occupait un continent qu'une carte
    # détaillée a déplacé. L'effacement croît doucement depuis le bord du
    # rectangle sur `fondu` unités, assez pour noyer les terres étroites en
    # suivant leur relief (pas de coupe droite), puis devient total au-delà.
    H_, W_ = champ.shape
    ys, xs = np.mgrid[0:H_, 0:W_].astype(np.float32)
    xs -= ouest
    # Un bruit lent déforme le bord des rectangles : là où ils coupent une terre,
    # la nouvelle côte ondule au lieu de suivre une droite.
    alea = np.random.default_rng(7)
    ondulation = cv2.GaussianBlur(alea.standard_normal((H_ // 4, W_ // 4)).astype(np.float32), (0, 0), 20)
    ondulation = cv2.resize(ondulation / ondulation.std() * 90, (W_, H_), interpolation=cv2.INTER_CUBIC)
    for x0, y0, x1, y1, fondu in CONFIG["cadre"].get("effacer", []):
        dedans = np.minimum.reduce([xs - x0, x1 - xs, ys - y0, y1 - ys]) + ondulation
        champ -= 60 * np.clip(dedans / fondu, 0, 1) + 2000 * np.clip(dedans / fondu - 1, 0, 1)
        effaces.append([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    del ys, xs
    for nom, ref in CONFIG["references"].items():
        if not ("points" in ref or "pose" in ref) or not ref.get("actif", True) or ref.get("methode") not in METHODES:
            continue
        masque = nettoyer(METHODES[ref["methode"]](ref), ref.get("aire_min", 40))
        h, w = masque.shape
        x0, y0, x1, y1 = ref["emprise"]
        emprise = np.zeros((h, w), np.uint8)
        emprise[y0:y1, x0:x1] = 1
        if "abords" in ref:
            # L'emprise se limite aux terres de la carte et à leurs abords :
            # la mer lointaine d'une carte détaillée ne doit rien effacer.
            r = ref["abords"]
            emprise &= cv2.dilate(masque, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
        for ex0, ey0, ex1, ey1 in ref.get("exclure", []):
            emprise[ey0:ey1, ex0:ex1] = 0
        if "pose" in ref:
            # Pose imposée, sans rotation : échelle et position du coin haut gauche.
            e, tx, ty = ref["pose"]
            m = np.array([[e, 0, tx], [0, e, ty]], np.float64)
        else:
            m = similitude(ref["points"])
            m = affiner(m, masque, emprise, base, k)
        echelle = np.hypot(*m[:, 0])
        mc = (m + decale).astype(np.float32)  # vers les colonnes du champ
        poids = np.clip(ndimage.distance_transform_edt(emprise) / ref.get("fondu", 60), 0, 1).astype(np.float32)
        if "fondu_bas" in ref:
            # Raccord plus long en bas de l'emprise, vers un continent que la carte ne montre qu'en partie.
            bas = np.clip((y1 - np.arange(h, dtype=np.float32)) / ref["fondu_bas"], 0, 1)[:, None]
            poids = np.minimum(poids, bas)
        distance = (ndimage.distance_transform_edt(masque) - ndimage.distance_transform_edt(1 - masque)).astype(np.float32)
        champ_d = cv2.warpAffine(distance * echelle, mc, (W, H), flags=cv2.INTER_LINEAR)
        poids = cv2.warpAffine(poids, mc, (W, H), flags=cv2.INTER_LINEAR)
        if ref.get("isolee"):
            # Une île entourée de mer : la version de la base est effacée sur
            # toute l'emprise (élargie), pour ne pas laisser de morceaux décalés.
            zone = cv2.warpAffine(emprise, mc, (W, H), flags=cv2.INTER_NEAREST)
            zone = cv2.dilate(zone, np.ones((2 * ref["isolee"] + 1,) * 2, np.uint8))
            champ[zone > 0] = np.minimum(champ[zone > 0], -4 * k)
        champ[:] = champ * (1 - poids) + champ_d * poids
        contour = max(cv2.findContours(cv2.dilate(emprise, np.ones((15, 15), np.uint8)), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)
        contour = cv2.approxPolyDP(contour, 4, True)[:, 0, :].astype(np.float64)
        recalages[nom] = {"matrice": np.round(m, 6).tolist(), "emprise": np.round(contour @ m[:, :2].T + m[:, 2], 1).tolist()}
        if "massifs" in ref:
            relief = massifs_teinte(ref, masque)
            contours, _ = cv2.findContours(relief, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                c = cv2.approxPolyDP(c, 3, True)[:, 0, :].astype(np.float64)
                if len(c) >= 3:
                    massifs.append(np.round(c @ m[:, :2].T + m[:, 2], 1).tolist())
        print(f"{nom} posée, échelle {echelle:.3f}")
    (CACHE / "recalages.json").write_text(json.dumps({"cartes": recalages, "massifs": massifs, "effaces": effaces}), encoding="utf-8")


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
    # Le cadre peut s'étendre à l'ouest de la carte de base (x négatifs), en mer.
    ouest = cadre.get("ouest", 0)
    champ = cv2.copyMakeBorder(champ, 0, 0, ouest, 0, cv2.BORDER_CONSTANT, value=-20.0)
    W += ouest
    poser_details(champ, terre, k, W, H, ouest)
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
        lisse = chaikin(simple, 2) - marge - [ouest, 0]
        anneaux.append({"trou": bool(parent != -1), "points": np.round(lisse, 1).tolist()})
    (CACHE / "cotes.json").write_text(json.dumps({"largeur": W, "hauteur": H, "ouest": ouest, "anneaux": anneaux}), encoding="utf-8")
    print(f"Repère {W} x {H}, {len(anneaux)} contours, {sum(len(a['points']) for a in anneaux)} points")


if __name__ == "__main__":
    main()
