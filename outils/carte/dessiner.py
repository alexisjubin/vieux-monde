"""Dessine le fond de la carte du monde (carte.svg) à partir des côtes et des éléments relevés.

Entrées : outils/carte/cache/cotes.json (construire.py) et
outils/carte/elements.json (montagnes, forêts, fleuves, lacs, marais, déserts
relevés en pixels de la carte de référence). Les couleurs ne sont pas dans le
SVG : chaque calque porte une classe, style.css les colore.

    .venv/Scripts/python.exe outils/carte/dessiner.py
"""

import json
import math
import random
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent.parent
CONFIG = json.loads((ICI / "references.json").read_text(encoding="utf-8"))
alea = random.Random(2522)


def chemin(points, ferme=True):
    p = np.asarray(points)
    d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in p)
    return d + ("Z" if ferme else "")


def courbe(points, ferme=False):
    """Catmull-Rom vers Béziers, pour les fleuves et les contours relevés à la main."""
    p = [tuple(q) for q in points]
    if len(p) < 3:
        return chemin(p, ferme)
    n = len(p)
    ext = (p[-1:] + p + p[:2]) if ferme else (p[:1] + p + p[-1:])
    d = f"M{ext[1][0]:.0f},{ext[1][1]:.0f}"
    for i in range(1, (n if ferme else n - 1) + 1):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.0f},{c1[1]:.0f} {c2[0]:.0f},{c2[1]:.0f} {p2[0]:.0f},{p2[1]:.0f}"
    return d + ("Z" if ferme else "")


def le_long(points, ecart):
    """Points régulièrement espacés le long d'une polyligne, avec la direction locale."""
    sortie, reste = [], 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        longueur = math.hypot(x2 - x1, y2 - y1)
        if not longueur:
            continue
        d = reste
        while d < longueur:
            t = d / longueur
            sortie.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, (x2 - x1) / longueur, (y2 - y1) / longueur))
            d += ecart
        reste = d - longueur
    return sortie


def pics(crete, largeur, k):
    """Petites montagnes à l'encre, semées autour de la crête et dessinées du fond vers l'avant.

    La chaîne s'affine à ses extrémités et sa largeur ondule, les plus hauts
    sommets sont sur la crête : on évite ainsi l'effet de bande régulière.
    """
    crete = [(x * k, y * k) for x, y in crete]
    points = le_long(crete, 4)
    if not points:
        return ""
    demi = largeur * k
    longueur = len(points) * 4
    phase, frequence = alea.uniform(0, 6.3), alea.uniform(1.5, 3.5)
    nombre = int(longueur * (2 * demi + 10) / 230)
    sommets = []
    for _ in range(nombre):
        i = alea.randrange(len(points))
        x, y, dx, dy = points[i]
        t = i / max(len(points) - 1, 1)
        profil = math.sin(math.pi * t) ** 0.5 * (0.75 + 0.25 * math.sin(phase + frequence * math.pi * t))
        u = alea.uniform(-1, 1)
        u = math.copysign(abs(u) ** 1.3, u)
        ecart = u * (demi * (0.3 + 0.7 * profil) + 5)
        h = (9 + 15 * (1 - abs(u)) ** 1.6 * (0.45 + 0.55 * profil)) * alea.uniform(0.8, 1.2)
        sommets.append((x - dy * ecart + alea.uniform(-3, 3), y + dx * ecart + alea.uniform(-3, 3), h))
    sommets.sort(key=lambda s: s[1])
    traits = []
    for x, y, h in sommets:
        l = h * alea.uniform(0.7, 0.95)
        pente = alea.uniform(-0.2, 0.2) * l
        d = f"M{x - l:.0f},{y:.0f}L{x + pente:.0f},{y - h:.0f}L{x + l:.0f},{y:.0f}Z"
        # Versant à l'ombre : une ou deux hachures, selon la taille du sommet.
        d += f"M{x + pente:.0f},{y - h:.0f}L{x + l * 0.3:.0f},{y:.0f}"
        if h > 17:
            d += f"M{x + pente + l * 0.3:.0f},{y - h * 0.55:.0f}L{x + l * 0.6:.0f},{y:.0f}"
        traits.append(f'<path d="{d}"/>')
    return "".join(traits)


def massif(contour):
    """Montagnes semées à l'intérieur d'un contour (massifs relevés sur une carte détaillée)."""
    sommets = []
    xs, ys = [p[0] for p in contour], [p[1] for p in contour]
    y = min(ys)
    while y < max(ys):
        x = min(xs)
        while x < max(xs):
            px, py = x + alea.uniform(-6, 6), y + alea.uniform(-4, 4)
            if alea.random() > 0.15 and dedans((px, py), contour):
                sommets.append((px, py, alea.uniform(10, 21)))
            x += 15
        y += 11
    sommets.sort(key=lambda s: s[1])
    traits = []
    for x, y, h in sommets:
        l = h * alea.uniform(0.7, 0.95)
        pente = alea.uniform(-0.2, 0.2) * l
        d = f"M{x - l:.0f},{y:.0f}L{x + pente:.0f},{y - h:.0f}L{x + l:.0f},{y:.0f}ZM{x + pente:.0f},{y - h:.0f}L{x + l * 0.3:.0f},{y:.0f}"
        traits.append(f'<path d="{d}"/>')
    return "".join(traits)


def hors_cartes_detaillees(elements, emprises, k):
    """Écarte les éléments relevés sur la base qui tombent dans l'emprise d'une carte détaillée."""
    def dans_une(points):
        pts = [(x * k, y * k) for x, y in points]
        return any(sum(dedans(p, e) for p in pts) > len(pts) / 2 for e in emprises)
    return {
        cle: [e for e in valeurs if not dans_une(e.get("crete") or e.get("contour") or e.get("trace"))]
        for cle, valeurs in elements.items() if isinstance(valeurs, list)
    }


def onduler(contour, k, amplitude=6):
    """Rend un contour relevé à la main plus irrégulier, comme un tracé à la plume."""
    poly = [(x * k, y * k) for x, y in contour]
    sortie = []
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        longueur = math.hypot(x2 - x1, y2 - y1) or 1
        n = max(1, int(longueur / 28))
        nx, ny = (y1 - y2) / longueur, (x2 - x1) / longueur
        for j in range(n):
            t = j / n
            d = 0 if j == 0 else alea.uniform(-amplitude, amplitude)
            sortie.append((x1 + (x2 - x1) * t + nx * d, y1 + (y2 - y1) * t + ny * d))
    return sortie


def semis(poly, pas_x, pas_y, motif, manque=0.12):
    """Répète un petit motif en rangs décalés et un peu désordonnés à l'intérieur d'un polygone."""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    traits, y, rang = [], min(ys) + pas_y / 2, 0
    while y < max(ys):
        x = min(xs) + (pas_x / 2 if rang % 2 else 0)
        while x < max(xs):
            px, py = x + alea.uniform(-pas_x * 0.3, pas_x * 0.3), y + alea.uniform(-pas_y * 0.25, pas_y * 0.25)
            if alea.random() > manque and dedans((px, py), poly):
                traits.append(motif(px, py))
            x += pas_x
        y += pas_y
        rang += 1
    return "".join(traits)


def arbre(x, y):
    r = alea.uniform(4.5, 6.5)
    return f"M{x - r:.0f},{y:.0f}a{r:.1f},{r * 1.1:.1f} 0 1,1 {2 * r:.1f},0Z"


def touffe(x, y):
    return f"M{x - 5:.0f},{y:.0f}h10M{x - 2:.0f},{y:.0f}l-2,-6M{x + 1:.0f},{y:.0f}v-7M{x + 3:.0f},{y:.0f}l2,-5"


def point(x, y):
    return f"M{x:.0f},{y:.0f}h1"


def dedans(pt, poly):
    x, y = pt
    vrai = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            vrai = not vrai
    return vrai


def main():
    cotes = json.loads((ICI / "cache" / "cotes.json").read_text(encoding="utf-8"))
    W, H = cotes["largeur"], cotes["hauteur"]
    terres = " ".join(chemin(a["points"]) for a in cotes["anneaux"])

    fichier_elements = ICI / "elements.json"
    elements = json.loads(fichier_elements.read_text(encoding="utf-8")) if fichier_elements.exists() else {}
    k = W / 1500
    fichier_recalages = ICI / "cache" / "recalages.json"
    recalages = json.loads(fichier_recalages.read_text(encoding="utf-8")) if fichier_recalages.exists() else {"cartes": {}, "massifs": []}
    emprises = [[tuple(p) for p in c["emprise"]] for c in recalages["cartes"].values()]
    elements = hors_cartes_detaillees(elements, emprises, k)

    calques = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
        "<defs>",
        f'<path id="trace-terres" d="{terres}" fill-rule="evenodd" clip-rule="evenodd"/>',
        '<clipPath id="terres"><use href="#trace-terres"/></clipPath>',
        '<filter id="grain" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="7"/>'
        '<feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.24  0 0 0 0 0.12  0 0 0 0.55 -0.12"/>'
        "</filter>",
        "</defs>",
        f'<rect class="mer" width="{W}" height="{H}"/>',
        '<use class="houle-large" href="#trace-terres"/>',
        '<use class="houle" href="#trace-terres"/>',
        '<use class="terre" href="#trace-terres"/>',
        f'<g clip-path="url(#terres)"><rect class="grain" width="{W}" height="{H}" filter="url(#grain)"/>',
    ]
    for d in elements.get("deserts", []):
        poly = onduler(d["contour"], k, 8)
        calques.append(f'<path class="desert" d="{courbe(poly, True)}"/>')
        calques.append(f'<path class="sable" d="{semis(poly, 16, 12, point, 0.35)}"/>')
    for m in elements.get("marais", []):
        poly = onduler(m["contour"], k, 6)
        calques.append(f'<path class="marais" d="{courbe(poly, True)}"/>')
        calques.append(f'<path class="touffes" d="{semis(poly, 26, 16, touffe, 0.3)}"/>')
    for f in elements.get("forets", []):
        poly = onduler(f["contour"], k, 7)
        calques.append(f'<path class="foret" d="{courbe(poly, True)}"/>')
        calques.append(f'<path class="arbres" d="{semis(poly, 14, 11, arbre)}"/>')
    for r in sorted(elements.get("fleuves", []), key=lambda r: -r.get("rang", 2)):
        calques.append(f'<path class="fleuve rang-{r.get("rang", 2)}" d="{courbe([(x * k, y * k) for x, y in r["trace"]])}"/>')
    for l in elements.get("lacs", []):
        calques.append(f'<path class="lac" d="{courbe([(x * k, y * k) for x, y in l["contour"]], True)}"/>')
    montagnes = sorted(elements.get("montagnes", []), key=lambda m: min(p[1] for p in m["crete"]))
    for m in montagnes:
        calques.append(f'<g class="relief">{pics(m["crete"], m.get("largeur", 6), k)}</g>')
    for contour in recalages["massifs"]:
        calques.append(f'<g class="relief">{massif([tuple(p) for p in contour])}</g>')
    calques += [
        "</g>",
        '<use class="cote" href="#trace-terres"/>',
        f'<rect class="bord" width="{W}" height="{H}"/>',
        "</svg>",
    ]
    sortie = RACINE / "carte.svg"
    sortie.write_text("\n".join(calques) + "\n", encoding="utf-8")
    print(f"{sortie} : {sortie.stat().st_size // 1024} Ko")


if __name__ == "__main__":
    main()
