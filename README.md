# ChessRoguelite

Jeu roguelite d'échecs (local, Windows) — **fenêtré** par défaut, **plein écran** optionnel, 
deck-builder de pièces entre manches, horloge à *ticks*, or par captures et ticks restants,
boutique d'améliorations, IA simple, pièce rare **Amazone** (Reine + Cavalier), sauvegarde méta.

## Prérequis
- Python 3.10+
- `pip install pygame`

## Lancer
```
python -m src.main
```
ou
```
python src/main.py
```

## Contrôles
- Souris : sélectionner une de vos pièces puis une destination (coups légaux surlignés).
- Espace : terminer votre tour s'il reste une action parallèle (rare).
- O : options in-game (plein écran / fenêtré).
- F : activer le mode *Freeze* ciblé si vous avez un consommable, puis cliquer une pièce ennemie.
- Échap : revenir en arrière / quitter un menu.

## Notes
- Départs : 5x5 → 6x6 → 7x7 → 8x8 (ensuite mode infini simple).
- Or : valeur classique (Pion=1, Fou/Cavalier=3, Tour=5, Dame=9, Amazone=12, Roi=0 mais prime fin de manche).
- Ticks : chaque coup coûte des ticks selon la pièce (configurable). Si vos ticks tombent à 0, vous perdez la manche.
- Boutique inter-manche : +ticks, -ticks adverses, ajouter/convertir pièce, chance de coût 0 par type, freeze (random/ciblé), doublement d'or, chances d'être Blanc/Noir, double coup initial.
- Sauvegarde : `save.json` dans `src/meta/` (deck, méta, déblocages).

Ce projet est un **prototype complet et modulaire** servant de base pro à étendre
(nouveaux objectifs, contenus, mécaniques).
