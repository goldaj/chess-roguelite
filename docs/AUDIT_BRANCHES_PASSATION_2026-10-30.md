# Audit Chess Roguelite : branches, produits, passation — 30/10/2026

## État Git : base `develop`
- `develop` (`90c5038f52f9743ab4f20885b120e5cf40d45442`) : branche active, conserver.
- `chatgpt/review-20261024` (`6df42335be322aaca9569f2c489b30fabbe22def`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. Candidate à nettoyage de référence sous réserve de liens/PR externes.
- `feat/chess-tactics-correct-rules-20261029` (`754e2a59cf2fbbfd3ceb2f8696acf0dc829b75dd`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. Candidate à nettoyage de référence sous réserve de liens/PR externes.
- `feat/gpt6-branching-campaign-20261027` (`9f297777b878b6fb47e6841f04f97a9211ac6097`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. Candidate à nettoyage de référence sous réserve de liens/PR externes.
- `feat/gpt6-windows-playtest-20261028` (`49b5fe6a584f6af84cc3a9b80c3f2e187e0f14ce`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. Candidate à nettoyage de référence sous réserve de liens/PR externes.
- `main` (`2faad3c811498f891f0683aaaf41e0d4dc614e54`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. **Ne pas supprimer sans vérifier consommateurs et déploiements malgré leur statut d'ancêtre.**
- `master` (`2faad3c811498f891f0683aaaf41e0d4dc614e54`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. **Ne pas supprimer sans vérifier consommateurs et déploiements malgré leur statut d'ancêtre.**
- `research/gpt6-tactical-ai-20261027` (`11de73504fa6694193d63cdbb225ac7398f14160`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. Candidate à nettoyage de référence sous réserve de liens/PR externes.
- `research/gpt6-tactical-ai-after-review-20261027` (`6bd51d87b67147a7ce24fa8bc837cd8ba9756075`) : **ahead 0** en comparaison GitHub du 30/10/2026, commit déjà ancêtre de `develop`. Candidate à nettoyage de référence sous réserve de liens/PR externes.

## PR
- [#5](https://github.com/goldaj/chess-roguelite/pull/5) : fusionnée ; `feat/chess-tactics-correct-rules-20261029` vers `feat/gpt6-windows-playtest-20261028`.
- [#4](https://github.com/goldaj/chess-roguelite/pull/4) : fusionnée ; `feat/gpt6-windows-playtest-20261028` vers `develop`.
- [#3](https://github.com/goldaj/chess-roguelite/pull/3) : fermée sans fusion directe ; `feat/gpt6-branching-campaign-20261027` vers `research/gpt6-tactical-ai-after-review-20261027`.
- [#2](https://github.com/goldaj/chess-roguelite/pull/2) : fermée sans fusion directe ; `research/gpt6-tactical-ai-after-review-20261027` vers `chatgpt/review-20261024`.
- [#1](https://github.com/goldaj/chess-roguelite/pull/1) : fermée sans fusion directe ; `chatgpt/review-20261024` vers `develop`.

## Challenger le jeu, pas seulement Git
- **Règles :** en passant, promotion et orientation des camps, captures et objectif de fin de partie ; vérifier recherche tactique sur au moins deux plies, états illégaux et transitions/ticks.
- **Campagne :** six rencontres, trois voies et boutique ; challenger les stratégies dominantes, finances, réussite des objectifs, équilibre sur seeds variées et joueurs novices. Les sparrings automatisés ne sont pas des taux de victoire humains.
- **Packaging Windows :** vérifier que l'exe PyInstaller utilise réellement les assets, que l'APK n'est pas évoqué à tort, que `save.json` du joueur ne soit pas écrasé, et que le lancement BAT soit simple sur machine Windows.
- **Différence branches :** anciennes PR #1-#3 fermées sans merge explicite mais intégrées par ascendance à `develop`. Les PR #4 et #5 ont été fusionnées. Ne pas rouvrir les PR empilées.

## Plan de reprise
Lire README (« ## Tester facilement les modifications sur Windows (PR #4, 28/10/2026) »), AGENTS.md, docs/BRANCHING_CAMPAIGN_BALANCE.md, docs/PLAYTEST_WINDOWS.md et historique. Exécuter `python -m unittest discover -s tests -p 'test_*.py' -v`, tests de non-régression règles puis le vrai jeu Windows. Vérifier assets, builds, temps d'installation et équilibrage humain avant livraison.

Aucun test ni simulation de gameplay lancé pendant cette passe, aucun code/fusion/suppression modifié : seulement cet audit statique. Les branches `main`/`master` requièrent décision humaine sur leur rôle avant suppression.
