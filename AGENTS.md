## Contribution de test rapide du 28/10/2026 : PR #4, Windows autonome

**PR #4** : https://github.com/goldaj/chess-roguelite/pull/4 ; branche `feat/gpt6-windows-playtest-20261028` **empilée sur PR #3**, elle-même sur PR #2 puis PR #1. Sans modification des règles, des ticks, de l'IA, des achats ou du contenu existant.

Cette branche ajoute `playtest_entry.py`, `LANCER_WINDOWS.bat`, `.github/workflows/windows-playtest.yml` et `docs/PLAYTEST_WINDOWS.md` : **un vrai exécutable Windows .exe produit et exécuté par la CI** (PyInstaller, dossier avec assets + content), et alternative BAT créant un venv. L'entrée redirige les écritures dans le **dossier playtest %LOCALAPPDATA%**, jamais dans le `save.json` de production. Le workflow doit réussir le smoke du **binaire compilé**, et publier un ZIP sous `ChessRoguelite-Windows-Playtest`, avant de le proposer.

**Pour Codex :** relire le guide, les checks du dernier HEAD, le test de sauvegarde isolée et la liste des artifacts. Ne pas fusionner PR #4 avant PR #3, ni prétendre qu'une version navigateur existe. Interventions très ciblées exclusivement sur le packaging et son exécution ; aucun code gameplay modifié.

---

## Avertissement Codex : PR #3 nouvelle campagne et équilibrage expérimental, 27/10/2026

Nouvelle branche **`feat/gpt6-branching-campaign-20261027`**, [PR #3](https://github.com/goldaj/chess-roguelite/pull/3) **brouillon, base `research/gpt6-tactical-ai-after-review-20261027` (PR #2)**, elle-même fille de PR #1.

C'est du **GAMEPLAY**, pas seulement des documents : six rencontres différentes, trois voies avec risques/récompenses, objectif de capture obligatoire pour gagner à l'épuisement des ticks ennemis (sauf tutoriel), boutique améliorée, pièces achetées conservées, anomalies de ticks/pouvoirs/or corrigées. **Toute modification de la règle de victoire est à faire valider en partie manuelle par le propriétaire avant merge**. Le réglage numérique actuel est une hypothèse expérimentale. Lire `docs/BRANCHING_CAMPAIGN_BALANCE.md` ; exécuter `python -m unittest discover -s tests -p 'test_*.py' -v`, le Pygame smoke et le diagnostic statique/autoplay. Les 36 sparrings à deck figé **ne sont pas des taux de victoire humains**. Aucun merge, VPS, prod ou sauvegarde du propriétaire touchés dans cette contribution.

---

## Contribution GPT6, 27/10/2026 : tactique réellement jouable

**PR #2** https://github.com/goldaj/chess-roguelite/pull/2, branche `research/gpt6-tactical-ai-after-review-20261027`, issue de `chatgpt/review-20261024` (PR #1 non fusionnée). Elle ajoute 3 niveaux d'IA à choix sauvegardé, une recherche tactique bornée et une consommation du gel sur exactement un tour adverse. Le handoff, preuves et limites sont dans `docs/TACTICAL_AI_DELIVERY.md`. Exécuter tests unitaires et smoke Pygame SDL dummy, ne pas attribuer ces modifications à `develop`. Ne pas modifier/écraser la PR #1 ni les sauvegardes personnelles. Diff/CI à revérifier au dernier HEAD avant fusion sélective.

# AGENTS.md — Chess Roguelite

Lire README.md puis **docs/CHATGPT_PROJECT_HISTORY.md** avant toute modification.

Projet : Jeu d'échecs avec progression et améliorations, Python/Pygame, interactions souris.

Validation et invariants : Lancer `python -m src.main` après installation pygame et pillow ; préserver save.json ignoré.

Préserver les fichiers existants ; ne pas inventer de résultats de test. Après chaque intervention, compléter le journal avec les nouveaux messages effectivement disponibles, en distinguant Utilisateur et Assistant, verbatim et résumé, dates vérifiées ou inconnues. Ne jamais inventer de conversation ou d'horodatage. Veiller au caractère public/privé du dépôt.



## Moteur tactique, 2026-10-29

Lire `docs/CHESS_RULES_AI.md`. `src/core/board.py` doit préserver les règles d'en passant et la promotion orientée selon `bottom_color` ; `src/core/ai.py` doit garder `choose_move(board,color)` et rester exécutable sans pygame. Tests : `python -m unittest discover -s tests -v`. Le code de l'interface et les sauvegardes locales ne sont pas modifiés par cette branche.


> Consolidation 29/10/2026 : PR #5 intégrée dans la branche unique PR #4 ; IA à trois difficultés et prise en passant de la PR #4 préservées.
