# Audit contradictoire et passation Chess Roguelite — 2026-10-30

État contrôlé à partir de la liste GitHub (9 branches), du graphe des commits, des 5 PR, du README et de AGENTS. Aucune partie de jeu ni suite de tests exécutée pendant cette passe.

## Branches et ascendance
- `develop` : `107e60ef7909b2a93c00a26f6c22cfe823afc223` : branche de référence, à conserver.
- `chatgpt/review-20261024` : **behind develop, 0 commit exclusif**. Travaux déjà compris dans develop ; candidat nettoyage seulement si plus de dépendance workflow/PR.
- `feat/chess-tactics-correct-rules-20261029` : **behind develop, 0 commit exclusif**. Travaux déjà compris dans develop ; candidat nettoyage seulement si plus de dépendance workflow/PR.
- `feat/gpt6-branching-campaign-20261027` : **behind develop, 0 commit exclusif**. Travaux déjà compris dans develop ; candidat nettoyage seulement si plus de dépendance workflow/PR.
- `feat/gpt6-windows-playtest-20261028` : **behind develop, 0 commit exclusif**. Travaux déjà compris dans develop ; candidat nettoyage seulement si plus de dépendance workflow/PR.
- `main` : **behind develop, 0 commit exclusif**. Ancienne branche de référence / alias historique à conserver jusqu'à vérification des consommateurs et de la politique de release.
- `master` : **behind develop, 0 commit exclusif**. Ancienne branche de référence / alias historique à conserver jusqu'à vérification des consommateurs et de la politique de release.
- `research/gpt6-tactical-ai-20261027` : **behind develop, 0 commit exclusif**. Travaux déjà compris dans develop ; candidat nettoyage seulement si plus de dépendance workflow/PR.
- `research/gpt6-tactical-ai-after-review-20261027` : **behind develop, 0 commit exclusif**. Travaux déjà compris dans develop ; candidat nettoyage seulement si plus de dépendance workflow/PR.

## PR recensées
- [#5](https://github.com/goldaj/chess-roguelite/pull/5) et [#4](https://github.com/goldaj/chess-roguelite/pull/4) : fusionnées.
- [#1](https://github.com/goldaj/chess-roguelite/pull/1), [#2](https://github.com/goldaj/chess-roguelite/pull/2), [#3](https://github.com/goldaj/chess-roguelite/pull/3) : clôturées sans merge explicite, mais leurs branches sont ancêtres de `develop`.

## Éléments observés
Racine : `.github`, `.gitignore`, `AGENTS.md`, `LANCER_WINDOWS.bat`, `README.md`, `assets`, `content`, `docs`, `playtest_entry.py`, `requirements.txt`, `src`, `tests`, `tools`.

README : ## Tester facilement les modifications sur Windows (PR #4, 28/10/2026)

**Version Windows prête à lancer, sans Python :** ouvrir [Build Windows playtest](https://github.com/goldaj/chess-roguelite/actions/workflows/windows-playtest.yml), choisir la dernière exécution **verte** de la branche `feat/gpt6-windows-playtest-20261028`, télécharger dans **Artifacts** le ZIP `ChessRoguelite-Windows-Playtest`, l'extraire et double-cliquer sur `ChessRoguelite-Playtest.exe`. Garder le dossier `_internal` à côté de l'EXE.

**Alternative avec Python :** télécharger le ZIP du code de cette branche, l'extraire et double-cliquer sur `LANCER_WINDOWS.bat`. Installation de Pygame/Pillow dans un venv propre au premier lancement, puis démarrages rapides.

**Les deux modes préservent la sauvegarde de production :** progression expérimentale dans `%LOCALAPPDATA%\ChessRoguelitePlaytest\save.json`. Le test concerne la campagne de la PR #3 ; aucune release ou fusion dans `develop`. Guide complet : [docs/PLAYTEST_WINDOWS.md](docs/PLAYTEST_WINDOWS.md). Une version navigateur n'est pas encore disponible ; elle exige un port spécifique du loop Pygame/persistance.

## Campagne à objectifs jouable et rééquilibrage expérimental (PR #3, 27/10/2026)

[PR #3](https://github.com/goldaj/chess-roguelite/pull/3) **brouillon empilée** sur [PR #2](https://github.com/goldaj/chess-roguelite/pull/2) : six adversaires distincts, mission de prises affichée pour gagner sur le temps, trois voies Équilibrée/Prudente/Audacieuse entre les manches, récompenses et budgets explicites, meilleure boutique et conservation de toutes les pièces achetées. La voie prudente gèle la pièce ennemie la plus forte pour son premier tour ; la voie audacieuse renforce l'ennemi et l'objectif c

AGENTS : ## Contribution de test rapide du 28/10/2026 : PR #4, Windows autonome

**PR #4** : https://github.com/goldaj/chess-roguelite/pull/4 ; branche `feat/gpt6-windows-playtest-20261028` **empilée sur PR #3**, elle-même sur PR #2 puis PR #1. Sans modification des règles, des ticks, de l'IA, des achats ou du contenu existant.

Cette branche ajoute `playtest_entry.py`, `LANCER_WINDOWS.bat`, `.github/workflows/windows-playtest.yml` et `docs/PLAYTEST_WINDOWS.md` : **un vrai exécutable Windows .exe produit et exécuté par la CI** (PyInstaller, dossier avec assets + content), et alternative BAT créant un venv. L'entrée redirige les écritures dans le **dossier playtest %LOCALAPPDATA%**, jamais dans le `save.json` de production. Le workflow doit réussir le smoke du **binaire compilé**, et publier un ZIP sous `ChessRoguelite-Windows-Playtest`, avant de le proposer.

**Pour Codex :** relire le guide, les checks du dernier HEAD, le test de sauvegarde isolée et la liste des artifacts. Ne pas fusionner PR

## Challenge fonctionnel et qualité
1. Tester réellement les règles échecs : échec au roi, mat, pat, prise en passant, promotion selon orientation, roque, répétitions et mouvements illégaux.
2. Tester la difficulté et le coût de l'IA tactique deux plis dans le jeu, pas seulement sur positions de test.
3. Mesurer équilibre de campagne 6 missions/3 voies, boutique et objectifs ; identifier les situations de soft-lock, stratégies dominantes et progressions impossibles.
4. Exécuter le playtest Windows et les tests headless ; relever les métriques, exceptions et exécutions reproductibles.
5. Ne jamais supprimer `main`/`master` simplement parce qu'elles sont ancêtres de `develop`. L'objectif est la réduction du nombre de branches de fonctionnalité devenues inutiles, pas la rupture d'anciens liens.
