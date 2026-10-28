# Tester la campagne de Chess Roguelite sous Windows, sans toucher à la production

**Branche :** \`feat/gpt6-windows-playtest-20261028\` ; dépend des PR #1, #2, #3, et doit être examinée en **PR #4**. Ce document décrit comment exécuter **la campagne expérimentale à six manches**, pas le code actuellement déployé sur \`develop\`.

## Option 1 : exécutable Windows prêt à lancer, sans Python

1. Ouvrir la [liste des exécutions du workflow **Build Windows playtest**](https://github.com/goldaj/chess-roguelite/actions/workflows/windows-playtest.yml). L'utilisateur doit être connecté à GitHub pour télécharger les artifacts.
2. Ouvrir la **dernière exécution verte sur la branche \`feat/gpt6-windows-playtest-20261028\`**. Éviter un binaire d'une autre branche.
3. Dans **Artifacts**, télécharger \`ChessRoguelite-Windows-Playtest\` (ZIP).
4. **Extraire entièrement le ZIP** dans un dossier ordinaire (par ex. \`Téléchargements\\ChessRoguelite-Test\`). Ne pas lancer l'EXE depuis l'intérieur du ZIP.
5. Double-cliquer sur \`ChessRoguelite-Playtest.exe\`. Ne pas séparer l'EXE du dossier \`_internal\` ou de ses ressources : elles sont nécessaires au jeu.
6. Jouer via la souris ; **Options** propose Facile, Normal, Difficile. Les boutiques entre manches permettent trois voies, et le compteur de captures est affiché à partir de la deuxième manche.

L'EXE est construit par GitHub Actions sur un runner Windows, avec PyInstaller en mode **dossier** et fichiers graphiques embarqués, sans runtime Python requis sur le PC. Le ZIP contient toute l'application, mais **pas de sauvegarde personnelle**.

**Windows SmartScreen :** un EXE non signé provenant d'une PR expérimentale peut déclencher l'avertissement Windows. Lire le fournisseur/origine et utiliser uniquement l'artifact créé par notre workflow de repo. Aucune garantie de signature ou de validation antivirus n'est revendiquée.

**Durée de disponibilité :** artifact GitHub conservé 30 jours ; relancer manuellement le workflow sur la branche si nécessaire. Le workflow peut aussi être déclenché depuis Actions → Build Windows playtest → Run workflow, en choisissant la branche (si GitHub l'expose selon la configuration du dépôt).

## Option 2 : lancer le code directement, avec Python (double-clic)

1. Télécharger [le ZIP de cette branche](https://github.com/goldaj/chess-roguelite/archive/refs/heads/feat/gpt6-windows-playtest-20261028.zip) et l'extraire.
2. Installer Python 3.11 ou 3.12 si absent. Pour Windows, vérifier que \`py -3\` ou \`python\` fonctionne dans un terminal.
3. **Double-cliquer sur \`LANCER_WINDOWS.bat\`** à la racine. Il crée \`.venv-playtest\`, installe Pygame/Pillow seulement la première fois, puis ouvre le jeu. Le premier démarrage a besoin d'Internet.
4. Au démarrage suivant, double-clic suffit. Si les dépendances sont mises à jour, supprimer le dossier \`.venv-playtest\` puis relancer le BAT.

Pour développer/tester sans fichier BAT :

\`\`\`powershell
py -3 -m venv .venv-playtest
.\.venv-playtest\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-playtest\Scripts\python.exe playtest_entry.py
\`\`\`

## Sauvegardes : isolation intentionnelle

Le lanceur et l'exécutable utilisent **leur propre sauvegarde** :

\`\`\`text
%LOCALAPPDATA%\\ChessRoguelitePlaytest\\save.json
\`\`\`

Cela ne modifie **pas** \`src/meta/save.json\` du code d'origine, ni la sauvegarde de ton installation en production. Les parties de test survivent au téléchargement d'une nouvelle version ; pour repartir de zéro, renommer ou supprimer **uniquement** ce fichier \`ChessRoguelitePlaytest\\save.json\`. Les erreurs locales sont écrites dans \`%LOCALAPPDATA%\\ChessRoguelitePlaytest\\last_crash.txt\` ; ne pas le committer, il peut contenir des chemins de fichiers locaux.

Pour comparer plusieurs versions avec des sauvegardes séparées, modifier explicitement la variable d'environnement \`CHESS_ROGUELITE_PLAYTEST_DATA_DIR\` (option pour développeurs) ; ne pas déplacer ni partager les sauvegardes par défaut.

## Limites

- **Web non livré à ce stade** : Pygame desktop et l'état de la sauvegarde ne sont pas directement compatibles avec un export HTML5. Une conversion pygbag/async du moteur, du rendu et de la persistance exigerait un projet distinct, et doit être testée réellement avant d'être annoncée.
- Le test automatique Windows utilise un affichage SDL simulé et la vraie pile Python/EXE. Il ne certifie pas une partie complète à la souris, ni l'équilibrage du jeu.
- **Aucune fusion en production, aucun déploiement, aucun changement de branche Codex**. Le binaire est un artifact CI temporaire, sans installateur et sans mises à jour automatiques.

## Retour de test utile au développeur

Pour les six manches, noter : manche / couleur / niveau IA / voie choisie / combien de ticks restaient au moment de gagner ou perdre / objectif de capture / argent et achats / temps de jeu et ressenti. Les 200 derniers combats terminés sont stockés **localement** dans la sauvegarde de test, sans envoi serveur. Le collecteur de statistiques ne voit pas les abandons et les sessions inachevées.

Analyse hors ligne facultative, depuis la racine du code :

\`\`\`powershell
py -3 tools/campaign_balance.py --save "$env:LOCALAPPDATA\\ChessRoguelitePlaytest\\save.json"
\`\`\`

Ne pas transmettre de sauvegarde complète sans vérifier ce qu'elle contient. Les conclusions sur l'équilibrage demandent de vraies parties, pas seulement les tests automatisés.
