# Historique ChatGPT de Chess Roguelite

**Archive partielle datée du 2026-10-24, à lire depuis AGENTS.md.** Les conversations complètes ne sont pas disponibles sous forme exportable dans cette session. Ne pas prétendre que ce fichier les remplace.

## Contexte confirmé dans README
Jeu d'échecs avec progression et améliorations, Python/Pygame, interactions souris.

## Reprise technique
Lancer `python -m src.main` après installation pygame et pillow ; préserver save.json ignoré.

## Échanges retrouvés
- **2026-10-18** — Assistant (résumé reconstruit, non verbatim) : archivage et classement de ce projet dans un dépôt autonome, en préservant le travail précédent.
- **2026-10-18 13:24:13 UTC** — Utilisateur (extrait exact) : « N'écrase aucun repo existant. »
- **2026-10-24** — Utilisateur (résumé fidèle, non verbatim ; heure inconnue) : souhaite AGENTS.md, un journal consultable par Codex avec échanges exacts, rôles, horodatages disponibles, et mise à jour de cette discipline à chaque modification Git.

## Limites
Aucun AGENTS.md initial. Il manque encore les questions et réponses intégrales des anciennes séances ; aucun message de l'assistant n'est inventé. Compléter depuis les exports authentiques si disponibles, avec examen préalable des données sensibles avant toute publication. Ajouter ensuite des entrées horodatées `Utilisateur (verbatim)` / `Assistant (verbatim)` lorsque les textes exacts sont accessibles.

## 2026-10-24 : revue multi-dépôts en parallèle de Codex (heure non attestée)

**Utilisateur (verbatim, conversation présente)**

> tu vois tout le boulot qu'on a fait sur la conversation Avancement projets codex ?
> Tu vas refaire la même chose sur TOUT mon repo git. Tu vas commencer par les projets les plus gros, regarder ce que tu peux faire dessus et le faire sur ta branch (même consignes que sur l'autre conversation).
> Tu vas ensuite me faire un rapport très succint des projets que t'as touché et de ce que t'as avancé dessus.
> Amuse toi !

**Assistant (résumé reconstruit, non verbatim)**

Sauvegardes meta écrites atomiquement (tempfile + os.replace), test de maintien de l'ancien fichier en cas d'erreur et CI de non-régression. Travail isolé sur `chatgpt/review-20261024`, base inchangée.

**Validation et confiance** : confiance élevée dans la modification ciblée ; ne pas supposer des tests locaux exécutés. Vérifier GitHub Actions et comparer avec le travail Codex avant intégration. Ne pas fusionner automatiquement. Aucun secret ou contenu privé de manuscrit ajouté.

## 2026-10-24 — Chess Roguelite: achat et transformation persistants

**Utilisateur (verbatim, heure de message non attestée)** : « je crois que ça a planté. Reprends là où tu t'es arrêté »

**Utilisateur (résumé reconstruit, non verbatim)** : souhaite réduire les changements de structure et favoriser les corrections fonctionnelles et la poursuite des fonctions non terminées, dans des branches indépendantes que Codex peut choisir de reprendre ou non.

**Assistant (résumé reconstruit, non verbatim)** : Les offres de la boutique se régénèrent seulement entre les manches et ne peuvent pas être rachetées plusieurs fois. Achat de pièces et conversion modifient réellement l'échiquier et la composition de l'armée, sans double débit de pièces d'or. Les transformations attendent une cible légale avant de débiter. L'Amazone reste verrouillée jusqu'à son déblocage. L'interface affiche les offres déjà achetées. Les précédents correctifs de prise en passant et promotion restent présents.

**Validation** : GitHub Actions du commit 563ce2b7033451353976b4d5cd70ce3a3404bb05: 10 tests réussis le 24 octobre 2026, y compris les appels des méthodes réelles de boutique testées sans affichage. Pas de test utilisateur graphique.

**Handoff Codex** : lire les changements sur `chatgpt/review-20261024`, poursuivre les éléments non terminés, puis choisir sélectivement les commits utiles. Aucun merge sur la branche principale.


## 2026-10-27 — Demande d'avancement fonctionnel réel sur un autre dépôt

**Utilisateur (verbatim accessible, heure précise inconnue)** :

> Ok. Un autre projet sur lequel tu peux intervenir pour faire avancer le projet ? Non bullshit, de l'avancement réel.
> Il y a genre 40 repo, et j'ai l'impression qu'on modifie toujours les mêmes.
> Je veux que ça apporte une grosse valeur fonctionnel au projet choisi, pour le projeti

**Assistant (résumé non verbatim)** : a inspecté des dépôts variés (jeux, Android, utilitaire de ROI, toolkit d'écriture, etc.) et retenu `chess-roguelite` plutôt que les dépôts déjà sollicités. Audit de [PR #1](https://github.com/goldaj/chess-roguelite/pull/1) avant de coder : la prise en passant, la promotion, la transformation et la sauvegarde y sont déjà corrigées. Pour ne pas réintroduire ces problèmes, nouvelle branche indépendante `research/gpt6-tactical-ai-after-review-20261027` et [PR #2](https://github.com/goldaj/chess-roguelite/pull/2) **brouillon, empilée sur PR #1**.

**Travail de gameplay livré** : IA tactique à trois difficultés, anticipation des réponses avec limite de noeuds, choix utilisateur depuis le menu Options et persistance de la difficulté ; correction des effets de gel (pièces gelées interdites un tour, possibilité pour les autres pièces de jouer). Un test démontre une prise de pion piégé par l'ancienne politique gourmande, évitée avec l'IA Normal. Suites de tests unitaires et smoke Pygame sous SDL dummy sur GitHub Actions, sans toucher aux données du joueur. Détails et limites : `docs/TACTICAL_AI_DELIVERY.md`.

**Limites explicites** : aucun test visuel humain ou partie complète, pas de garantie de performance sur grosses armées, pas de modification de règles de pat/checkmate, pas de nouvelle publication en production. Les anciens échanges non récupérés restent des résumés partiels, pas des transcriptions imaginaires.


## 2026-10-27 — L'utilisateur demande une progression de fonctionnalités et insiste sur l'équilibrage

**Utilisateur (verbatim exact de la présente conversation, heure non attestée)** :
> J'ai l'impression que t'as fait une amélioration intéressante, mais c'est ok non plus un avancement pour aller plus loin dans l'avancement du développement des fonctionnalités du logiciel. Je pense que tous les logiciels du repo attendent encore de grandes améliorations pour aller plus loin et faire des choses à très fortes valeurs ajoutées.

**Utilisateur (verbatim exact, précision intercalée pendant la contribution)** :
> Et si tu continues sur des jeux, pense bien à l'équilibrage du jeu. Notamment celui-ci, je n'ai toujours pas trouvé un équilibrage pertinent même en prod aujourd'hui

**Assistant (résumé non verbatim)** : a créé la branche dédiée `feat/gpt6-branching-campaign-20261027`, [PR #3](https://github.com/goldaj/chess-roguelite/pull/3) empilée sur PR #2 sans toucher à la branche de Codex ou `develop`. A construit un véritable chapitre de campagne de six manches avec formations, missions de captures, trois routes, gel défensif et prime de risque ; corrigé les anomalies du premier budget 100 ticks puis de 12–22, bonus achat écrasé, gel/double-coup à durée incorrecte, tick ennemi mal orienté, achat d'or non plafonné, perte silencieuse de pièces par placement et boutiques sans choix abordable. Instrumentation locale anonyme bornée des combats finis et CLI optionnelle pour analyser les sauvegardes sans les transmettre. Un test déterministe de 36 combats **IA Facile contre IA Facile, deck fixe et sans boutique**, a trouvé 34 succès passifs initiaux par épuisement des ticks ; a ensuite révisé les règles pour qu'une mission de prise soit obligatoire sauf au tutoriel. Cette expérience ne constitue **ni une validation de l'équilibrage humain ni un test de la production**. Les tests CI et Pygame simulé de la PR doivent être relus au dernier HEAD avant adoption. Recherche/complément de Codex : tests manuels sur les six manches, choix de l'objectif de victoire, calibrage per-difficulté et observation d'abandons. Tout reste en brouillon, aucune fusion/déploiement et aucune modification des données utilisateur.


## 2026-10-27 — Reprise après interruption et clôture demandée

**Utilisateur (verbatim exact, conversation présente, heure non attestée)** :
> T'as crash. Fini proprement ce que tu faisais. Documente tout pour le prochain qui travaille dessus. Et arrête toi proprement après.

**Assistant (résumé non verbatim des actions exécutées après la reprise)** : a retrouvé la PR #3 `feat/gpt6-branching-campaign-20261027` et ses trois workflows verts sur `a662b0903b520dfd17f852e589b131264929dc42`. A vérifié le détail du job CI `campaign-logic` (46 tests Python 3.12 réussis, ainsi que les scripts de diagnostic et 36 sparrings synthétiques) et `campaign-pygame` (succès du vrai jeu sous affichage SDL simulé). A inspecté les modules `src/main.py`, `src/core/campaign.py`, `src/core/formation.py`, tests, diff de PR et feuille de route du projet. A complété `docs/BRANCHING_CAMPAIGN_BALANCE.md`, section 8, avec consignes opérationnelles de reprise et limites, sans modifier de nouvelle règle de jeu. Toute validation après les commits de clôture doit être relue au HEAD final. **Le jeu n'est pas déclaré équilibré pour des joueurs réels** ; PR #3 conservée en brouillon, pas de fusion, aucune sauvegarde personnelle manipulée. Clôture demandée ; arrêter les développements ici.


## 2026-10-28 — Demande de lancement facile sur poste / éventuellement Web

**Utilisateur (verbatim exact, conversation présente, heure non attestée)** :
> tu peux aussi me faire quelque chose pour que je puisse facilement lancer le programme sur mon poste, voire en web, pour que j'arrive à tester rapidement tes modifs

**Assistant (résumé non verbatim)** : plutôt que modifier la campagne figée, a créé la branche `feat/gpt6-windows-playtest-20261028` et la PR #4 empilée sur PR #3. A ajouté un double-clic `LANCER_WINDOWS.bat` (venv dédié) et surtout un workflow GitHub Windows qui installe les dépendances, construit via PyInstaller un **exécutable et ses ressources** et **exécute ce vrai .exe** avec SDL dummy/automatisation avant de fournir un ZIP artifact utilisable sans Python. Le point d'entrée `playtest_entry.py` crée une sauvegarde playtest distincte sous LocalAppData sans toucher aux sauvegardes existantes. Documentation de téléchargement/utilisation dans `docs/PLAYTEST_WINDOWS.md`, tests de cloisonnement de sauvegarde et CI sur la branche. **Port Web non réalisé : Pygame desktop nécessite un chantier spécifique HTML5/persistance ; ne pas l'annoncer comme disponible.** Aucun changement de règle, IA, équilibrage ou déploiement sur `develop`; PR laissée en brouillon.



## 2026-10-29 : règles et IA

Utilisateur (verbatim, date de ce fil, heure individuelle inconnue) : « Je ne te demande pas de créer une tâche planifiée qui continue chaque jour. Je te demande de continuer maintenant en boucle et de ne pas t'arrêter sur juste 3 améliorations alors qu'il y a plus de 40 repo et plusieurs améliorations possibles par repo ».

Assistant (résumé non verbatim) : quatrième rotation de dépôts, intervention sur `chess-roguelite` pour corriger prise en passant, promotion lorsque les noirs sont en bas et adversaire anticipant un demi-coup ennemi. Tests purs sans Pygame, CI et documentation `docs/CHESS_RULES_AI.md`. L'exécution graphique interactive demeure non validée.


> Consolidation 29/10/2026 : PR #5 intégrée dans la branche unique PR #4 ; IA à trois difficultés et prise en passant de la PR #4 préservées.
