# Le Vieux Monde, une chronologie

Chronologie sourcée de l'univers de Warhammer Fantasy et de The Old World, des Anciens à la Fin des Temps, avec une carte du monde zoomable. Plus de 500 événements, filtrables par faction, région, lieu, importance et fiabilité, en français, anglais et allemand. Site statique sans dépendance ni étape de build, publié sur `alexisjubin.com/vieux-monde/`.

## Lancer en local

Les données sont chargées par `fetch`, il faut donc un serveur :

```
python -m http.server 8742
```

puis ouvrir http://localhost:8742.

## Données

- `donnees/referentiel.json` : âges, régions, factions et niveaux de fiabilité. Tous les identifiants utilisés dans les événements viennent d'ici. `epoque_tow` délimite la bande hachurée de l'époque The Old World.
- `donnees/evenements-*.json` : les événements, un objet par entrée.
- `donnees/carte.json` : généré, ne pas modifier à la main. Les lieux de la chronologie, les colonies et les provinces, dans le repère de `carte.svg` (5760 unités de large).
- `carte.svg` : le fond de carte, généré. C'est un tracé redessiné dans notre propre style, aucune image de référence n'est publiée.

## Carte

La carte se construit avec les scripts de `outils/carte/`, dans un environnement Python à part :

```
uv venv .venv
uv pip install --python .venv/Scripts/python.exe opencv-python-headless scikit-image numpy pillow scipy
.venv/Scripts/python.exe outils/carte/construire.py
.venv/Scripts/python.exe outils/carte/dessiner.py
.venv/Scripts/python.exe outils/carte/lieux.py
```

1. `construire.py` extrait le trait de côte de la carte de référence (`references/ie-monde.webp`, la carte du monde de Total War: Warhammer III). Il sépare terre et mer avec des graines de mer posées à la main dans `references.json` et les 617 colonies de la carte interactive (`references/ie-factions.json`) comme graines de terre.
2. `dessiner.py` dessine `carte.svg` à partir des côtes et des éléments relevés à la main dans `elements.json` (montagnes, forêts, fleuves, lacs, marais, déserts).
3. `lieux.py` place les lieux de `lieux.json` (par le nom de la colonie correspondante ou par une position relevée), ajoute les colonies, les provinces et les grands noms de `etiquettes.json`.

Le dossier `references/` reste en local : il contient des cartes de Games Workshop et de Creative Assembly qui ne doivent pas être publiées. `outils/carte/apercu.html` affiche le fond de carte seul, avec `?vue=x,y,largeur,hauteur` pour zoomer.

Tous les textes affichés existent en trois langues, sous la forme `{ "fr": ..., "en": ..., "de": ... }`. Une chaîne simple est acceptée pour ce qui ne se traduit pas (titre d'un livre anglais). Les textes de l'interface sont dans `TEXTES`, en tête de `app.js`.

Champs d'un événement :

| Champ | Contenu |
| --- | --- |
| `id` | identifiant court, sert d'ancre (`#chute-de-karak-huit-pics`) |
| `annee`, `fin` | années du Calendrier Impérial, négatives avant Sigmar. `fin` vaut `null` pour un événement ponctuel |
| `approx` | `true` si la date est approximative |
| `ere`, `regions`, `factions` | identifiants du référentiel |
| `lieux` | identifiants de `carte.json`, peut être vide |
| `importance` | 3 tournant majeur, 2 important, 1 détail |
| `fiabilite` | `etabli`, `divergent` ou `incertain` |
| `titre`, `resume` | textes trilingues |
| `note` | divergences entre sources, conversions de calendrier, trilingue ou `""` |
| `sources` | liste de `{ titre, detail, url }`, le livre officiel d'abord quand il est connu. `titre` et `detail` peuvent être trilingues |

Les résumés sont rédigés à la main, aucune phrase n'est copiée des sources.

## Filtres partageables

Les filtres sont gardés dans l'adresse : `?faction=nains&region=montagnes&lieu=karaz-a-karak&importance=3` ou `#id-evenement` pour pointer un événement. `?lang=en` force une langue, sinon le site la demande à la première visite et la retient dans le navigateur.
