## Contribution GPT6, 27/10/2026 : tactique réellement jouable

**PR #2** https://github.com/goldaj/chess-roguelite/pull/2, branche `research/gpt6-tactical-ai-after-review-20261027`, issue de `chatgpt/review-20261024` (PR #1 non fusionnée). Elle ajoute 3 niveaux d'IA à choix sauvegardé, une recherche tactique bornée et une consommation du gel sur exactement un tour adverse. Le handoff, preuves et limites sont dans `docs/TACTICAL_AI_DELIVERY.md`. Exécuter tests unitaires et smoke Pygame SDL dummy, ne pas attribuer ces modifications à `develop`. Ne pas modifier/écraser la PR #1 ni les sauvegardes personnelles. Diff/CI à revérifier au dernier HEAD avant fusion sélective.

# AGENTS.md — Chess Roguelite

Lire README.md puis **docs/CHATGPT_PROJECT_HISTORY.md** avant toute modification.

Projet : Jeu d'échecs avec progression et améliorations, Python/Pygame, interactions souris.

Validation et invariants : Lancer `python -m src.main` après installation pygame et pillow ; préserver save.json ignoré.

Préserver les fichiers existants ; ne pas inventer de résultats de test. Après chaque intervention, compléter le journal avec les nouveaux messages effectivement disponibles, en distinguant Utilisateur et Assistant, verbatim et résumé, dates vérifiées ou inconnues. Ne jamais inventer de conversation ou d'horodatage. Veiller au caractère public/privé du dépôt.
