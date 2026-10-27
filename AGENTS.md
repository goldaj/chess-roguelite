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
