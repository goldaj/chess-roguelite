# Adversaire tactique et gel, implémentation réelle (27 octobre 2026)

## Ce qui change pour le joueur

L'adversaire n'est plus limité à l'ancienne décision opportuniste de capture immédiate. Dans **Options**, un nouveau bouton alterne entre trois comportements :

| Niveau | Comportement |
| --- | --- |
| **Facile** | Prend le coup légal le plus intéressant immédiatement, par valeur de pièce capturée, sans anticiper. |
| **Normal** (par défaut) | Étudie son coup puis la meilleure réponse adverse (deux demi-coups). Cela évite certains sacrifices évidents. |
| **Difficile** | Étudie également le coup suivant et utilise l'élagage alpha-bêta (trois demi-coups), avec un plafond de noeuds pour ne pas bloquer indéfiniment l'interface. |

Le choix est sauvegardé dans la clé `ai_difficulty` du fichier méta existant, **sans casser les anciennes sauvegardes**. Une préférence absente ou inconnue revient à Normal. Le niveau peut être modifié entre deux parties **ou pendant une partie** via Options, sans perdre la progression.

**Gel réellement utilisable :** une pièce ennemie gelée est exclue de la sélection de l'IA pendant son prochain tour. Si une autre pièce peut jouer, l'ennemi joue avec celle-ci ; si toutes les pièces sont gelées, le tour est passé. À la fin de ce tour, le gel est retiré automatiquement. Avant, l'IA pouvait choisir une pièce gelée et perdre le tour même en ayant des alternatives, et le gel pouvait persister.

## Ce qui fonctionne effectivement

- `src/core/ai.py` : coups fournis par **le vrai `Board.legal_moves_for`**, pas un deuxième ensemble de règles. Prend en charge l'Amazone, les plateaux variables, la promotion automatique, la prise en passant issue de PR #1, le roi capturable du roguelite, les pièces gelées.
- Recherche déterministe à profondeur limitée ; plafonds initiaux de **450 noeuds normal** et **1 400 noeuds difficile**. Ce sont des choix de performance provisoires, **pas une garantie de temps réel en millisecondes**.
- Évaluation matérielle/positionnelle simplifiée et prévision des captures/réponses. N'est **pas** un moteur d'échecs classique, et ne promet ni ELO ni optimisation de jeu parfaite.
- `src/main.py` : vraie modification de l'interface Options et du tour adverse ; sauvegarde atomique existante réutilisée telle quelle.
- Aucune modification des systèmes d'économie, de manches, ticks, boutique, sauvegarde méta existante ni des assets artistiques.

## Vérification CI reproductible

```bash
# Sans dépendances graphiques
python -m unittest discover -s tests -p 'test_*.py' -v

# Avec pygame et Pillow installés, seulement dans un environnement isolé
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=. python tests/smoke_pygame.py
```

**Tests effectivement observés :**
- **25 tests unitaires/headless réussis**, dont tests anciens (boutique, promotion, en passant, sauvegarde), tactiques et méthodes applicatives d'Options/gel ; scénario vérifié où le niveau facile capture un pion défendu que Normal évite.
- **Pygame smoke réussi** : vraie initialisation App, rendu, menu Options, changement sauvegardé de difficulté, démarrage d'une manche et animation d'un coup adverse, avec une sauvegarde en répertoire temporaire.
- **CI GitHub Python 3.12 / Pygame 2.6.1** : runs réussis au commit `9e69a9e`, [push](https://github.com/goldaj/chess-roguelite/actions/runs/40576700062), et PR associées.
- Tests rapides sur matrices conçues, **pas de test d'une campagne complète de six manches**, ni mesure robuste du temps maximal d'un coup sur tous les ordres de grandeur d'armée.

Le premier test d'intégration de l'interface a échoué parce que le substitut de jeu dans les tests ne définissait pas `toggle_fullscreen`, méthode sans rapport avec l'IA. Corrigé dans le harness, aucun bug produit identifié. La première exécution du smoke Pygame a échoué faute du chemin de module `src` dans l'environnement CI. Corrigée par `PYTHONPATH=.`, puis retestée verte. Conserver cette trace d'audit.

## Dépendance de branche et consignes à Codex

- Base technique **[PR #1](https://github.com/goldaj/chess-roguelite/pull/1)**, branche `chatgpt/review-20261024`, qui a déjà corrigé en passant, promotion, transformations et sauvegarde.
- Contribution actuelle **[PR #2](https://github.com/goldaj/chess-roguelite/pull/2)**, branche `research/gpt6-tactical-ai-after-review-20261027`, **brouillon**. Ne pas fusionner directement sur `develop` avant d'assimiler PR #1, ou reprendre sélectivement avec base cohérente.
- Les limites ne doivent pas être cachées : aucun test visuel humain, aucun ELO, aucun benchmark FPS sous Windows dans toutes les configurations. Un algorithme limité en noeuds peut conserver des erreurs tactiques et être lent sur des positions très denses.
- Ordre de reprise : lire `AGENTS.md`, ce document, les tests `tests/test_tactical_ai.py` / `tests/test_ai_app_integration.py` et `tests/smoke_pygame.py` ; tester une partie manuellement, mesurer latence des difficultés sur manches tardives, puis décider des plafonds et de la logique de pat/checkmate du roguelite.
- Cette PR **ne change volontairement pas les règles existantes** qui font passer un tour à l'ennemi sans coups légaux, ni les ticks ni la règle de capture du roi, pour ne pas transformer le jeu sans validation du design.

## Critère de clôture du présent sous-jalon

Fonctionnalité réellement accessible dans le menu, enregistrement persistant, gel corrigé et IA testée. Une vraie partie avec ressenti joueur, le réglage des équilibres et l'amélioration stratégique future sont des jalons différents et non revendiqués comme achevés.
