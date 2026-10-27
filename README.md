## Campagne à objectifs jouable et rééquilibrage expérimental (PR #3, 27/10/2026)

[PR #3](https://github.com/goldaj/chess-roguelite/pull/3) **brouillon empilée** sur [PR #2](https://github.com/goldaj/chess-roguelite/pull/2) : six adversaires distincts, mission de prises affichée pour gagner sur le temps, trois voies Équilibrée/Prudente/Audacieuse entre les manches, récompenses et budgets explicites, meilleure boutique et conservation de toutes les pièces achetées. La voie prudente gèle la pièce ennemie la plus forte pour son premier tour ; la voie audacieuse renforce l'ennemi et l'objectif contre plus d'or.

Un audit a identifié les victoires passives aux ticks et plusieurs achats à effet inversé. Ils sont corrigés sur la branche expérimentale, sans prétendre que **le jeu est déjà correctement équilibré en production**. Les vrais combats terminés alimentent des statistiques **locales**, analysables volontairement hors ligne. Voir [docs/BRANCHING_CAMPAIGN_BALANCE.md](docs/BRANCHING_CAMPAIGN_BALANCE.md) et les tests CI. Ne pas fusionner PR #3 avant PR #2 et PR #1.

## Nouveauté du prototype sur PR #2 : adversaire tactique (27/10/2026)

La [PR #2](https://github.com/goldaj/chess-roguelite/pull/2) ajoute **trois difficultés d'IA accessibles dans Options** : Facile (capture immédiate), Normal (anticipe la réponse) et Difficile (anticipe deux réponses, recherche bornée). Le niveau est conservé dans la sauvegarde méta, avec compatibilité des anciennes sauvegardes.

Les pouvoirs de gel ont un vrai effet pendant un tour : l'IA choisit une autre pièce si possible, puis le gel expire. **25 tests unitaires et un démarrage Pygame simulé** ont été exécutés en CI ; le ressenti d'une partie complète reste à tester. Cette PR est empilée sur [PR #1](https://github.com/goldaj/chess-roguelite/pull/1) et n'est pas fusionnée à `develop` ; la documentation précise est dans [docs/TACTICAL_AI_DELIVERY.md](docs/TACTICAL_AI_DELIVERY.md).

# Chess Roguelite — échecs et progression

Version améliorée (assets lisibles type chess.com, shop aléatoire 3 choix, plateau initial 8x3, coordonnées, UI boutons + animations).

## Prérequis
- Python 3.10+
- `pip install pygame pillow`

## Lancer
```
python -m src.main
```
ou
```
python src/main.py
```

Tout se pilote **à la souris** (boutons).
La progression personnelle (`src/meta/save.json`) reste sur le poste et est ignorée par Git. Le jeu crée son état local au besoin ; aucun fichier personnel ne doit être ajouté pour lancer le prototype.

## Situer ce prototype parmi les autres jeux

| Projet | Expérience explorée | Organisation du code |
| --- | --- | --- |
| [Moonrail](https://github.com/goldaj/moonrail-narrative-deckbuilder) | Deckbuilding narratif, collection et progression persistante | Projet distinct, avec sa direction de produit et ses personnages |
| [Bestiaire](https://github.com/goldaj/roguelite-bestiary-deckbuilder) | Créatures, cartes et attrition persistante au fil des combats | Prototype autonome, moteur `core/` et tests ; progression encore à corriger |
| [DeckLite](https://github.com/goldaj/decklite-roguelite-deckbuilder) | Construire son deck pendant une run, choisir des récompenses, événements et boutique méta | Prototype Pygame concentré dans `main.py` |
| [Exploration sur tuiles](https://github.com/goldaj/tilemap-exploration-roguelite) | Se déplacer sur une grille, rencontrer des ennemis, gérer objets et boutique | Modules monde/combat/interface, tuiles et sprites |
| [Chess Roguelite](https://github.com/goldaj/chess-roguelite) | Déplacer des pièces d'échecs et acquérir des améliorations entre les affrontements | Plateau, IA, progression et interface souris |
| [Idle Clicker](https://github.com/goldaj/idle-clicker-tkinter) | Clics, revenus et achats avec coût dynamique | Interface de bureau Tkinter/ttkbootstrap |

Ces dépôts conservent des expériences distinctes, à différents niveaux d'avancement.
