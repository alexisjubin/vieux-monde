# Le Vieux Monde, une chronologie

Chronologie sourcée de l'univers de Warhammer Fantasy et de The Old World, des Anciens à la Fin des Temps, avec une carte du Vieux Monde. Filtrable par faction, région, lieu et fiabilité, en français, anglais et allemand. Site statique sans dépendance ni étape de build, publié sur `alexisjubin.com/vieux-monde/`.

## Lancer en local

Les données sont chargées par `fetch`, il faut donc un serveur :

```
python -m http.server 8742
```

puis ouvrir http://localhost:8742.

## Données

- `donnees/referentiel.json` : âges, régions, factions et niveaux de fiabilité. Tous les identifiants utilisés dans les événements viennent d'ici. `epoque_tow` délimite la bande hachurée de l'époque The Old World.
- `donnees/evenements-*.json` : les événements, un objet par entrée.
- `donnees/carte.json` : les lieux de la carte (coordonnées dans le repère 1000 x 780 de `carte.svg`) et les noms de régions, reliefs et mers. Les lieux `lointain` sont des flèches vers les terres hors de la carte.
- `carte.svg` : le fond de carte, généré par `python outils/dessiner_carte.py`. C'est un tracé libre d'après la géographie officielle, pas une copie des cartes de Games Workshop.

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

Les filtres sont gardés dans l'adresse : `?faction=nains&region=montagnes&lieu=karaz-a-karak` ou `#id-evenement` pour pointer un événement. `?lang=en` force une langue, sinon le site la demande à la première visite et la retient dans le navigateur.
