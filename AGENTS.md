# AGENTS.md — Chess Roguelite

Lire README.md puis **docs/CHATGPT_PROJECT_HISTORY.md** avant toute modification.

Projet : Jeu d'échecs avec progression et améliorations, Python/Pygame, interactions souris.

Validation et invariants : Lancer `python -m src.main` après installation pygame et pillow ; préserver save.json ignoré.

Préserver les fichiers existants ; ne pas inventer de résultats de test. Après chaque intervention, compléter le journal avec les nouveaux messages effectivement disponibles, en distinguant Utilisateur et Assistant, verbatim et résumé, dates vérifiées ou inconnues. Ne jamais inventer de conversation ou d'horodatage. Veiller au caractère public/privé du dépôt.

## Moteur tactique, 2026-10-29

Lire `docs/CHESS_RULES_AI.md`. `src/core/board.py` doit préserver les règles d'en passant et la promotion orientée selon `bottom_color` ; `src/core/ai.py` doit garder `choose_move(board,color)` et rester exécutable sans pygame. Tests : `python -m unittest discover -s tests -v`. Le code de l'interface et les sauvegardes locales ne sont pas modifiés par cette branche.
