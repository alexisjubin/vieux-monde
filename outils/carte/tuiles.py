"""Découpe le fond de carte (carte.svg) en tuiles d'image pour le site.

Le site n'affiche plus le SVG lui-même : ses dizaines de milliers de montagnes
rendaient chaque zoom lent. On le rend ici une fois pour toutes, avec les
couleurs de style.css, à plusieurs niveaux de détail :
- fond.webp, la carte entière à 0,5 pixel par unité, toujours affichée ;
- tuiles/<niveau>/<colonne>-<ligne>.webp, des tuiles de 512 pixels à 1, 2 et
  4 pixels par unité, chargées par app.js selon le zoom et la zone visible.

    .venv/Scripts/python.exe outils/carte/tuiles.py
"""

import io
import json
import math
import re
import shutil
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "tuiles"
TAILLE = 512
NIVEAUX = [1, 2, 4]
APERCU = 0.5
BLOC = 2048  # rendu par blocs de 4 x 4 tuiles
QUALITE = 80


def page(svg, largeur, hauteur):
    style = (RACINE / "style.css").read_text(encoding="utf-8")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{style}
html, body {{ margin: 0; background: transparent; }}
.carte {{ width: {largeur}px; height: {hauteur}px; overflow: hidden; }}
.carte svg {{ width: {largeur}px; height: {hauteur}px; will-change: auto; }}
</style></head><body><div class="carte">{svg}</div></body></html>"""


def rendre(onglet, x, y, l, h, px_l, px_h):
    """Rend la zone (x, y, l, h) de la carte en une image de px_l x px_h pixels."""
    onglet.set_viewport_size({"width": px_l, "height": px_h})
    onglet.evaluate(
        "([v, w, h]) => { const s = document.querySelector('svg'); s.setAttribute('viewBox', v);"
        " s.style.width = w + 'px'; s.style.height = h + 'px'; s.parentNode.style.width = w + 'px'; s.parentNode.style.height = h + 'px'; }",
        [f"{x} {y} {l} {h}", px_l, px_h],
    )
    png = onglet.screenshot(clip={"x": 0, "y": 0, "width": px_l, "height": px_h})
    return Image.open(io.BytesIO(png)).convert("RGB")


def enregistrer(image, chemin):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    image.save(chemin, "WEBP", quality=QUALITE, method=5)
    return chemin.stat().st_size


def main():
    svg = (RACINE / "carte.svg").read_text(encoding="utf-8")
    largeur, hauteur = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    total = 0
    with sync_playwright() as p:
        navigateur = p.chromium.launch(channel="msedge", headless=True)
        onglet = navigateur.new_page(device_scale_factor=1)
        onglet.set_content(page(svg, BLOC, BLOC))

        px_l, px_h = round(largeur * APERCU), round(hauteur * APERCU)
        total += enregistrer(rendre(onglet, 0, 0, largeur, hauteur, px_l, px_h), SORTIE / "fond.webp")

        for niveau in NIVEAUX:
            cote = TAILLE / niveau  # côté d'une tuile, en unités de la carte
            colonnes, lignes = math.ceil(largeur / cote), math.ceil(hauteur / cote)
            par_bloc = BLOC // TAILLE
            for bj in range(0, lignes, par_bloc):
                for bi in range(0, colonnes, par_bloc):
                    image = rendre(onglet, bi * cote, bj * cote, BLOC / niveau, BLOC / niveau, BLOC, BLOC)
                    for j in range(bj, min(bj + par_bloc, lignes)):
                        for i in range(bi, min(bi + par_bloc, colonnes)):
                            # Les tuiles du bord droit et du bas s'arrêtent au bord de la carte.
                            l = min(cote, largeur - i * cote) * niveau
                            h = min(cote, hauteur - j * cote) * niveau
                            x0, y0 = (i - bi) * TAILLE, (j - bj) * TAILLE
                            tuile = image.crop((x0, y0, x0 + round(l), y0 + round(h)))
                            total += enregistrer(tuile, SORTIE / str(niveau) / f"{i}-{j}.webp")
            print(f"niveau {niveau} : {colonnes} x {lignes} tuiles")
        navigateur.close()

    manifeste = {"largeur": largeur, "hauteur": hauteur, "taille": TAILLE, "niveaux": NIVEAUX, "apercu": APERCU}
    (SORTIE / "tuiles.json").write_text(json.dumps(manifeste) + "\n", encoding="utf-8")
    print(f"{total / 1e6:.1f} Mo au total")


if __name__ == "__main__":
    main()
