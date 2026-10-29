# Le Vieux Monde, une chronologie

Chronologie sourcée de l'univers de Warhammer Fantasy et de The Old World, filtrable par faction, région et fiabilité. Site statique sans dépendance ni étape de build, publié sur `alexisjubin.com/vieux-monde/`.

## Lancer en local

Les données sont chargées par `fetch`, il faut donc un serveur :

```
python -m http.server 8742
```

puis ouvrir http://localhost:8742.

## Données

- `donnees/referentiel.json` : âges, régions, factions et niveaux de fiabilité. Tous les identifiants utilisés dans les événements viennent d'ici. `epoque_tow` délimite la bande hachurée de l'époque The Old World.
- `donnees/evenements-*.json` : les événements, un objet par entrée.

Champs d'un événement :

| Champ | Contenu |
| --- | --- |
| `id` | identifiant court, sert d'ancre (`#chute-de-karak-huit-pics`) |
| `annee`, `fin` | années du Calendrier Impérial, négatives avant Sigmar. `fin` vaut `null` pour un événement ponctuel |
| `approx` | `true` si la date est approximative |
| `ere`, `regions`, `factions` | identifiants du référentiel |
| `importance` | 3 tournant majeur, 2 important, 1 détail |
| `fiabilite` | `etabli`, `divergent` ou `incertain` |
| `note` | divergences entre sources, conversions de calendrier |
| `sources` | liste de `{ titre, detail, url }`, le livre officiel d'abord quand il est connu |

Les résumés sont rédigés à la main, aucune phrase n'est copiée des sources.

## Filtres partageables

Les filtres sont gardés dans l'adresse : `?faction=nains&region=montagnes` ou `#id-evenement` pour pointer un événement.
