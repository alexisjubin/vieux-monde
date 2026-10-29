"""Bibliothèque de montagnes dessinées : lavis au pinceau et trait de plume.

Chaque montagne est un <symbol> SVG, base posée sur y = 0, sommet vers le haut,
large d'environ 100 unités. Elle est faite de plusieurs couches :
- une ombre au pied, en lavis très léger ;
- la silhouette, remplie de la couleur du relief pour masquer les montagnes de derrière ;
- le lavis du versant à l'ombre, en trois passes décalées pour un bord de pinceau ;
- la calotte de neige pour la famille « neige » ;
- le trait d'encre : contour effilé aux extrémités, arêtes et hachures qui descendent la pente.

Les couleurs passent par des variables CSS (--carte-relief, --carte-lavis,
--carte-encre, --carte-neige), héritées à travers <use>.

    .venv/Scripts/python.exe outils/carte/montagnes.py   # écrit cache/planche-montagnes.html
"""

import math
import random
from pathlib import Path

ICI = Path(__file__).resolve().parent

# (famille, nombre, hauteur, demi-largeur, nombre de sommets, neige)
FAMILLES = [
    ("pic", 12, (62, 80), (46, 58), (1, 1), False),
    ("massif", 12, (55, 72), (60, 78), (2, 3), False),
    ("mont", 10, (40, 54), (40, 52), (1, 2), False),
    ("neige", 8, (64, 82), (50, 66), (1, 2), True),
    ("colline", 8, (16, 26), (34, 46), (1, 1), False),
]


def trait_effile(points, largeur, alea):
    """Polygone d'un trait de plume : fin aux deux bouts, plus épais au milieu, un peu irrégulier."""
    n = len(points)
    gauche, droite = [], []
    for i, (x, y) in enumerate(points):
        a = points[max(i - 1, 0)]
        b = points[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        lg = math.hypot(dx, dy) or 1
        nx, ny = -dy / lg, dx / lg
        t = i / (n - 1)
        w = largeur * (0.15 + 0.85 * math.sin(math.pi * t) ** 0.7) * alea.uniform(0.85, 1.15) / 2
        gauche.append((x + nx * w, y + ny * w))
        droite.append((x - nx * w, y - ny * w))
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in gauche + droite[::-1]) + "Z"


def versant(depart, arrivee, courbure, alea, pas=7):
    """Points d'un versant entre deux points, creusé (concave) et un peu irrégulier."""
    (x0, y0), (x1, y1) = depart, arrivee
    n = max(3, int(math.hypot(x1 - x0, y1 - y0) / pas))
    monte = y1 < y0
    pts = []
    for i in range(n + 1):
        t = i / n
        f = t ** courbure if monte else 1 - (1 - t) ** courbure
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * f
        if 0 < i < n:
            x += alea.uniform(-1.2, 1.2)
            y += alea.uniform(-1.2, 1.2)
        pts.append((x, y))
    return pts


def sur_contour(contour, x):
    """Hauteur du contour (points de gauche à droite) à l'abscisse x."""
    for (x1, y1), (x2, y2) in zip(contour, contour[1:]):
        if x1 <= x <= x2 and x2 > x1:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return 0.0


def chemin(points):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z"


def montagne(famille, hauteurs, largeurs, nb_sommets, neige, alea):
    h = alea.uniform(*hauteurs)
    w = alea.uniform(*largeurs)
    colline = famille == "colline"
    n = alea.randint(*nb_sommets)

    # Sommets répartis sur la largeur, le plus haut au milieu, séparés par des cols.
    sommets = []
    for i in range(n):
        cx = (((i + 0.5) / n) * 1.1 - 0.55) * w if n > 1 else alea.uniform(-0.15, 0.15) * w
        cx += alea.uniform(-0.06, 0.06) * w
        ch = h * (1 if i == n // 2 else alea.uniform(0.62, 0.85))
        sommets.append((cx, -ch))
    courbure = 0.85 if colline else alea.uniform(1.15, 1.45)
    contour = versant((-w, 0), sommets[0], courbure, alea)
    for a, b in zip(sommets, sommets[1:]):
        col = ((a[0] + b[0]) / 2 + alea.uniform(-4, 4), max(a[1], b[1]) * alea.uniform(0.55, 0.72))
        contour += versant(a, col, 1.2, alea)[1:] + versant(col, b, 1.2, alea)[1:]
    pied_droit = (w * alea.uniform(0.9, 1.05), 0)
    contour += versant(sommets[-1], pied_droit, courbure, alea)[1:]
    if colline:
        contour = [(x, y * (0.75 + 0.25 * math.cos(x / w * math.pi / 2))) for x, y in contour]

    couches = [
        f'<ellipse cx="{w * 0.1:.1f}" cy="1.5" rx="{w * 1.08:.1f}" ry="{max(3, h * 0.08):.1f}" style="fill:var(--carte-lavis);opacity:.2"/>',
        f'<path d="{chemin(contour)}" style="fill:var(--carte-relief)"/>',
    ]
    encre = [trait_effile(contour, 2.0 if colline else 2.5, alea)]

    # Pour chaque sommet : une arête vers le pied, le versant de droite est à l'ombre.
    aretes = []
    for i, (sx, sy) in enumerate(sommets):
        droite = sommets[i + 1][0] if i + 1 < len(sommets) else pied_droit[0]
        pied = (sx + (droite - sx) * alea.uniform(0.25, 0.45), 0)
        arete = versant((sx, sy), pied, 1.0, alea, pas=6)
        arete = [(x + 0.1 * w * math.sin(math.pi * j / (len(arete) - 1)), y) for j, (x, y) in enumerate(arete)]
        aretes.append((arete, droite, sy))
        bord = sorted([(x, y) for x, y in contour if sx < x <= droite], key=lambda p: -p[0])
        ombre = arete + bord
        for passe in range(3):
            pts = []
            for x, y in ombre:
                if neige and y < sy * 0.68:
                    y = sy * 0.68 + alea.uniform(-2, 2)
                pts.append((x + alea.uniform(-1.8, 1.8), y + alea.uniform(-1.8, 1.8)))
            couches.append(f'<path d="{chemin(pts)}" style="fill:var(--carte-lavis);opacity:{0.17 + 0.07 * passe:.2f}"/>')
        if not colline:
            encre.append(trait_effile(arete, 1.7, alea))

    # Neige : calotte claire au-dessus d'une ligne en dents de scie.
    if neige:
        for sx, sy in sommets:
            limite = sy * 0.68
            gauche_x = next((x for x, y in contour if y <= limite and x <= sx), sx - 8)
            droite_x = next((x for x, y in reversed(contour) if y <= limite and x >= sx), sx + 8)
            dents = [(gauche_x, limite)]
            for j in range(1, 5):
                xj = gauche_x + (droite_x - gauche_x) * j / 5
                dents.append((xj, limite + (5 if j % 2 else -1) + alea.uniform(-1.5, 1.5)))
            dents.append((droite_x, limite))
            calotte = [(x, y) for x, y in contour if gauche_x <= x <= droite_x and y <= limite + 0.5]
            couches.append(f'<path d="{chemin(calotte + dents[::-1])}" style="fill:var(--carte-neige)"/>')
            encre.append(trait_effile(dents, 1.1, alea))

    # Hachures dans l'ombre : de l'arête vers le contour de droite, en descendant, sans en sortir.
    for arete, droite, sy in aretes:
        nombre = 3 if colline else alea.randint(5, 9)
        for i in range(nombre):
            t = (i + 0.7) / (nombre + 0.5)
            k = min(int(t * (len(arete) - 1)), len(arete) - 1)
            x0, y0 = arete[k]
            if neige and y0 < sy * 0.68:
                continue
            x1 = x0 + (droite - x0) * alea.uniform(0.45, 0.8)
            y1 = min(0, max(y0 + (x1 - x0) * 0.55, sur_contour(contour, x1) + 2.5))
            if y1 <= y0 + 1:
                continue
            milieu = ((x0 + x1) / 2, (y0 + y1) / 2 + alea.uniform(-1, 1))
            encre.append(trait_effile([(x0 + 1.2, y0 + 0.8), milieu, (x1, y1)], alea.uniform(0.9, 1.3), alea))
    # Quelques traits au pied pour poser la montagne sur le sol.
    for _ in range(alea.randint(1, 3)):
        x = alea.uniform(-w * 0.9, w * 0.9)
        encre.append(trait_effile([(x - 6, 1.5), (x, 2.3), (x + 6, 1.5)], 1.0, alea))
    couches.append(f'<path d="{"".join(encre)}" style="fill:var(--carte-encre)"/>')
    return "".join(couches), h, w


def bibliotheque(graine=1979):
    """Renvoie [(identifiant, famille, svg, hauteur, demi_largeur)]."""
    alea = random.Random(graine)
    sortie = []
    for famille, nombre, hauteurs, largeurs, sommets, neige in FAMILLES:
        for i in range(nombre):
            svg, h, w = montagne(famille, hauteurs, largeurs, sommets, neige, alea)
            sortie.append((f"m-{famille}-{i}", famille, svg, h, w))
    return sortie


def defs(montagnes):
    return "".join(f'<symbol id="{ident}" overflow="visible">{svg}</symbol>' for ident, _, svg, _, _ in montagnes)


def planche():
    """Planche d'essai : toute la bibliothèque, puis une chaîne de démonstration."""
    montagnes = bibliotheque()
    cases = []
    for i, (ident, _, _, _, _) in enumerate(montagnes):
        cases.append(f'<use href="#{ident}" transform="translate({70 + (i % 10) * 125} {110 + (i // 10) * 120})"/>')
    # Chaîne : grands sommets au centre, collines au bord, dessinés du fond vers l'avant.
    alea = random.Random(7)
    chaine = []
    for _ in range(130):
        t = alea.random()
        ecart = alea.gauss(0, 1)
        centre = max(0.0, 1 - abs(ecart) / 2.2) * math.sin(math.pi * t) ** 0.5
        famille = alea.choice(["pic", "massif"]) if centre > 0.55 else "mont" if centre > 0.25 else "colline"
        ident = alea.choice([m for m in montagnes if m[1] == famille])[0]
        e = 0.45 + 0.35 * centre
        chaine.append((780 + ecart * 38 + math.sin(t * 6) * 20, ident, 120 + t * 1000, e, alea.random() < 0.5))
    for y, ident, x, e, miroir in sorted(chaine):
        cases.append(f'<use href="#{ident}" transform="translate({x:.0f} {y:.0f}) scale({-e if miroir else e:.2f} {e:.2f})"/>')
    page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Planche des montagnes</title>
<style>
:root {{ --carte-relief: #dcc08c; --carte-lavis: #6b4a2a; --carte-encre: #3e2a17; --carte-neige: #f1e6cc; }}
body {{ margin: 0; background: #d8b884; }}
svg {{ display: block; width: 100%; height: auto; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 920">
<defs>{defs(montagnes)}</defs>
{"".join(cases)}
</svg></body></html>
"""
    sortie = ICI / "cache" / "planche-montagnes.html"
    sortie.write_text(page, encoding="utf-8")
    print(f"{len(montagnes)} montagnes, planche : {sortie}")


if __name__ == "__main__":
    planche()
