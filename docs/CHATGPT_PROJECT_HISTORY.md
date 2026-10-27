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
