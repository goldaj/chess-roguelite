# Audit GitHub et passation — 2026-10-30

**Portée vérifiée :** liste des branches et PR ouvertes sur GitHub. **Non vérifié :** tests, CI et contenu complet de chaque diff. Aucune branche déclarée supprimable sur le seul critère de son nom.

- Dépôt : `goldaj/chess-roguelite` ; branche par défaut : `develop`.
- PR ouvertes : aucune.

## Branches (9)
- `chatgpt/review-20261024`
- `develop` (défaut)
- `feat/chess-tactics-correct-rules-20261029`
- `feat/gpt6-branching-campaign-20261027`
- `feat/gpt6-windows-playtest-20261028`
- `main`
- `master`
- `research/gpt6-tactical-ai-20261027`
- `research/gpt6-tactical-ai-after-review-20261027`

## Points de vigilance pour le prochain agent
- Préserver les règles d'échecs, l'équilibrage, les assets et les builds jouables ; vérifier les anciennes PR empilées et la cible develop.
- Comparer chaque branche à sa cible réelle (SHA, ascendance, commits exclusifs, fichiers modifiés), puis seulement proposer des suppressions.
- Examiner PR clôturées, versions déployées, workflows et dépendances interbranches.
- Rejouer les tests applicables avant fusion et protéger la production.
- Conserver les résultats de recherche et les preuves, même quand une PR a été clôturée.

**Décision :** aucune suppression ou fusion automatique autorisée par ce seul inventaire.
