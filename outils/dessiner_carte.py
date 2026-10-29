"""Dessine le fond de carte du Vieux Monde (carte.svg).

Le tracé est une interprétation libre de la géographie officielle : côtes,
reliefs, forêts et fleuves. Les noms et les lieux ne sont pas dans le SVG,
app.js les pose par-dessus à partir de donnees/carte.json, dans la langue
choisie.

    python outils/dessiner_carte.py
"""

import math
import random
from pathlib import Path

LARGEUR, HAUTEUR = 1000, 780
alea = random.Random(1979)

CONTINENT = [
    (60, 300), (95, 268), (150, 250), (200, 238), (262, 248), (330, 232),
    (378, 242), (408, 258), (440, 226), (500, 206), (560, 192), (622, 182),
    (672, 166), (722, 142), (782, 112), (840, 84), (884, 40), (900, -10),
    (1010, -10), (1010, 790), (790, 790), (782, 748), (752, 724), (716, 716),
    (690, 732), (664, 752), (622, 758), (582, 746), (548, 752), (512, 774),
    (494, 790), (478, 790), (470, 752), (452, 712), (440, 664), (424, 622),
    (402, 600), (378, 618), (366, 668), (346, 722), (310, 772), (250, 778),
    (190, 770), (140, 748), (102, 708), (88, 652), (104, 604), (96, 566),
    (86, 520), (80, 458), (92, 406), (76, 360), (62, 330),
]

NORSCA = [
    (170, -10), (186, 30), (230, 76), (290, 104), (360, 124), (430, 134),
    (500, 124), (560, 110), (620, 96), (680, 82), (740, 66), (800, 46),
    (850, 26), (900, 4), (910, -10),
]

ALBION = [(30, 120), (70, 96), (112, 112), (124, 160), (104, 210), (64, 226), (32, 196), (22, 156)]
SARTOSA = [(552, 756), (566, 750), (578, 758), (570, 770), (554, 770)]

RELIEFS = {
    "bord-du-monde": [(872, 30), (850, 120), (832, 220), (818, 300), (806, 380),
                      (812, 470), (826, 550), (842, 630), (834, 700), (822, 770)],
    "grises": [(384, 290), (370, 350), (356, 420), (352, 480), (366, 540), (392, 590)],
    "noires": [(430, 580), (500, 584), (570, 570), (640, 578), (712, 576), (790, 588)],
    "irrana": [(120, 598), (180, 604), (240, 598), (300, 604), (352, 600)],
    "apuccini": [(498, 616), (516, 662), (534, 708)],
    "milieu": [(560, 252), (586, 244), (608, 254)],
    "orcal": [(214, 344), (240, 356), (232, 376)],
    "norsca": [(250, 30), (330, 52), (400, 48)],
    "norsca-est": [(560, 44), (640, 40), (720, 30)],
    "deuil": [(912, 470), (930, 540), (946, 610)],
}

FORETS = {
    "drakwald": [(430, 296), (470, 284), (498, 300), (488, 326), (446, 330)],
    "ombres": [(580, 214), (640, 204), (666, 228), (628, 246), (584, 240)],
    "grande": [(560, 360), (640, 350), (676, 384), (630, 410), (566, 398)],
    "reikwald": [(420, 380), (448, 368), (462, 396), (432, 410)],
    "arden": [(140, 416), (196, 406), (214, 440), (168, 456), (136, 444)],
    "loren": [(296, 496), (338, 488), (350, 530), (316, 552), (290, 530)],
    "chalons": [(240, 292), (270, 286), (276, 306), (248, 312)],
}

FLEUVES = {
    "reik": [(568, 576), (548, 524), (540, 476), (516, 424), (484, 354), (460, 310), (432, 282), (410, 262)],
    "talabec": [(810, 322), (744, 330), (684, 322), (630, 332), (572, 344), (484, 354)],
    "stir": [(808, 432), (744, 430), (684, 424), (626, 442), (578, 462), (540, 476)],
    "aver": [(748, 584), (700, 540), (652, 508), (594, 494), (542, 482)],
    "lynsk": [(800, 190), (752, 196), (712, 186), (684, 172)],
    "brienne": [(340, 472), (290, 486), (230, 474), (170, 482), (102, 480)],
    "grismerie": [(330, 300), (296, 280), (262, 262)],
}

FRONTIERES = [
    [(640, 236), (700, 238), (760, 246), (812, 250)],
]


def lisser(points, ferme):
    """Courbe de Catmull-Rom convertie en Béziers cubiques."""
    n = len(points)
    if ferme:
        p = points[-1:] + points + points[:2]
    else:
        p = points[:1] + points + points[-1:]
    d = f"M{p[1][0]:.1f},{p[1][1]:.1f}"
    fin = n if ferme else n - 1
    for i in range(1, fin + 1):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d + (" Z" if ferme else "")


def dechiqueter(points, ferme, amplitude=4.0, pas=14):
    """Ajoute des points intermédiaires légèrement décalés, pour un trait de côte irrégulier."""
    sortie = []
    paires = list(zip(points, points[1:] + points[:1])) if ferme else list(zip(points, points[1:]))
    for (x1, y1), (x2, y2) in paires:
        longueur = math.hypot(x2 - x1, y2 - y1)
        etapes = max(1, int(longueur / pas))
        nx, ny = (y1 - y2) / (longueur or 1), (x2 - x1) / (longueur or 1)
        for k in range(etapes):
            t = k / etapes
            decalage = 0 if k == 0 else alea.uniform(-amplitude, amplitude)
            sortie.append((x1 + (x2 - x1) * t + nx * decalage, y1 + (y2 - y1) * t + ny * decalage))
    if not ferme:
        sortie.append(points[-1])
    return sortie


def le_long(points, ecart):
    """Points régulièrement espacés le long d'une ligne brisée, avec leur direction."""
    resultat = []
    reste = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        longueur = math.hypot(x2 - x1, y2 - y1)
        d = reste
        while d < longueur:
            t = d / longueur
            resultat.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, (x2 - x1) / longueur, (y2 - y1) / longueur))
            d += ecart
        reste = d - longueur
    return resultat


def montagnes(points):
    """Petits pics serrés le long de la ligne de crête, dessinés du fond vers l'avant."""
    pics = []
    for x, y, dx, dy in le_long(points, 9):
        for cote in (-1, 1):
            if alea.random() < 0.25:
                continue
            ecart = alea.uniform(2, 8)
            pics.append((x - dy * cote * ecart, y + dx * cote * ecart, alea.uniform(7, 11)))
    pics.sort(key=lambda p: p[1])
    traits = []
    for ox, oy, h in pics:
        l = h * 0.7
        traits.append(f'<path d="M{ox - l:.1f},{oy + h / 2:.1f} L{ox:.1f},{oy - h / 2:.1f} L{ox + l:.1f},{oy + h / 2:.1f} Z"/>'
                      f'<path class="ombre" d="M{ox:.1f},{oy - h / 2:.1f} L{ox + l * 0.35:.1f},{oy + h / 2:.1f}"/>')
    return f'<g class="relief">{"".join(traits)}</g>'


def arbres(contour):
    xs, ys = [p[0] for p in contour], [p[1] for p in contour]
    ronds = []
    y = min(ys)
    while y < max(ys):
        x = min(xs) + alea.uniform(0, 6)
        while x < max(xs):
            if dedans((x, y), contour):
                ronds.append(f"M{x - 2.6:.1f},{y:.1f} a2.6,2.6 0 1,1 5.2,0")
            x += alea.uniform(7, 10)
        y += 7
    return f'<path class="foret" d="{lisser(contour, True)}"/><path class="arbres" d="{" ".join(ronds)}"/>'


def dedans(pt, poly):
    x, y = pt
    vrai = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            vrai = not vrai
    return vrai


def main():
    terres = [dechiqueter(t, True) for t in (CONTINENT, NORSCA, ALBION, SARTOSA)]
    chemins_terre = " ".join(lisser(t, True) for t in terres)

    morceaux = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGEUR} {HAUTEUR}">',
        '<defs><clipPath id="cadre"><rect width="1000" height="780"/></clipPath></defs>',
        '<g clip-path="url(#cadre)">',
        f'<rect class="mer" width="{LARGEUR}" height="{HAUTEUR}"/>',
        f'<path class="houle" d="{chemins_terre}"/>',
        f'<path class="terre" d="{chemins_terre}"/>',
    ]
    for contour in FORETS.values():
        morceaux.append(arbres(contour))
    for ligne in FLEUVES.values():
        morceaux.append(f'<path class="fleuve" d="{lisser(dechiqueter(ligne, False, 2.5, 18), False)}"/>')
    for ligne in FRONTIERES:
        morceaux.append(f'<path class="frontiere" d="{lisser(ligne, False)}"/>')
    for ligne in RELIEFS.values():
        morceaux.append(montagnes(ligne))
    morceaux += ["</g>", f'<rect class="bord" width="{LARGEUR}" height="{HAUTEUR}"/>', "</svg>"]

    sortie = Path(__file__).resolve().parent.parent / "carte.svg"
    sortie.write_text("\n".join(morceaux) + "\n", encoding="utf-8")
    print(f"{sortie} : {sortie.stat().st_size} octets")


if __name__ == "__main__":
    main()
