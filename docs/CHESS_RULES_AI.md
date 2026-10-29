# Chess Roguelite : règles corrigées + adversaire tactique (2026-10-29)

## Nouvelles fonctionnalités

### Échecs et règles du plateau

Le pion qui avance de deux cases définit désormais la case temporaire `en_passant`. Un pion adjacent peut capturer en passant **au coup immédiatement suivant** : le pion capturé est retiré de la colonne voisine. Si un autre coup est joué entre-temps, l'occasion expire. Les coups illégaux sans pion adverse adjacent ne sont pas proposés.

Les promotions de pion sont déterminées par l'orientation `bottom_color`, pas par l'hypothèse « blancs en bas ». Le jeu peut attribuer aléatoirement le camp joueur ; ceci corrige la promotion du camp placé en bas lorsqu'il est noir.

Les règles de vérification d'échec sont inchangées, et l'en passant est vérifié dans les clones d'essais pour éviter les mouvements qui exposent le roi.

### IA adverse tactique

L'adversaire ne choisit plus seulement la prise ayant la plus forte valeur immédiate. Il examine chaque coup légal et sa meilleure réponse adverse (2 demi-coups), calcule un score matériel et privilégie la décision qui évite les reprises évidentes. Une faible prime favorise les prises à évaluation égale. L'algorithme demeure **simple, déterministe, sans apprentissage machine** et ne calcule ni mat en N ni stratégie profonde.

Le contrat `choose_move(board,color)` reste inchangé pour l'interface Pygame.

## Tester

```bash
python -m unittest discover -s tests -v
python -m src.main
```

Tests sans dépendances graphiques pour les règles dans `tests/test_chess_rules.py`. GitHub Actions valide Python 3.10/3.12. Les essais interactifs Pygame restent à faire sur le poste local.

## Passation Codex

- Ne pas modifier la sauvegarde personnelle `src/meta/save.json`.
- Compléter les tests de roque, promotion choisie et échec/pat. Les limites historiques de la mécanique d'échecs doivent être auditées sans présumer d'une conformité FIDE complète ; c'est un roguelite à règles propres.
- Mesurer le coût du 2-ply sur des plateaux 8×8 plus densément peuplés. Passer à un cache de positions ou une recherche alpha-beta limitée seulement après benchmark.
- Ajouter un choix de difficulté (IA aléatoire, gourmande, tactique) avec retour clair au joueur.
- Évaluer aussi la qualité et le rythme de la progression roguelite, sans confondre amélioration de l'IA avec équilibrage global.
