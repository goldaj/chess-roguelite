# Chess Roguelite : campagne à objectifs, voies et mesure d'équilibrage

**27 octobre 2026, PR indépendante expérimentale empilée sur l'IA tactique GPT6.**
C'est une vraie modification du jeu, pas uniquement un plan. **Aucun prétendu « équilibrage validé humainement »** : les paramètres ci-dessous sont un premier profil testable, conçu après avoir détecté des contradictions de l'économie et de la règle de victoire. L'acceptation par Codex et par un joueur reste indispensable.

## 1. Pourquoi la campagne d'origine était difficile à équilibrer

Constats directement vérifiables dans le code de départ :

- La première manche ignorait son budget de 12 ticks configuré en commençant à **100/100 ticks** ; les manches suivantes redescendaient brutalement à **14–22**.
- Les adversaires des six manches commençaient tous avec **Roi + 3 pions**, les renforts 1–3 étaient tirés aléatoirement. Il y avait peu de structure d'apprentissage ni de boss identifiable.
- Les deux armées étaient replacées par deux fonctions dupliquées, limitées à certains emplacements ; **les pions/achats supplémentaires pouvaient être silencieusement perdus**.
- Acheter « -10 % ticks ennemi » baissait en réalité le coût du coup ennemi (0,9 au lieu de 1), donc **l'aidait à survivre plus longtemps**.
- « Double coup au début de prochaine manche » restait actif pour toutes les manches suivantes.
- « Doubler l'or » pouvait devenir exponentiel aux boutiques successives sans plafond.
- Les trois offres du marchand étaient tirées sans garantir une option **abordable**, même si le joueur avait assez d'or pour une option du catalogue.
- Des bonus de ticks achetés pouvaient être écrasés lorsque le nouveau combat était préparé.
- Les achats de biais Blanc/Noir en pleine run étaient inutiles : la couleur est tirée une seule fois à l'entrée de la run et ces biais ne sont pas sauvegardés dans les améliorations permanentes.
- **Surtout**, une victoire était accordée dès épuisement des ticks ennemis, même sans prise : dans un banc déterministe très simplifié (deux agents niveau Facile, aucun achat/pouvoir), **34 combats sur 36 aboutissaient à une victoire automatique du joueur sur le temps**, parce que ses ticks de départ étaient supérieurs. C'est un **test d'alarme sur les règles**, absolument PAS une estimation du taux de victoire d'une personne réelle.

## 2. Nouvelles six rencontres jouables

| Manche | Adversaire | Pièces ennemies hors Roi | Ticks joueur / ennemi | Objectif matériel minimal | Récompense de base |
| --- | --- | --- | --- | --- | --- |
| 1 | Les éclaireurs | 3 P | 22 / 16 | 0 : tutoriel survie | 10 or |
| 2 | La cavalerie | 3 P + 1 N | 23 / 18 | 2 points | 12 or |
| 3 | Les archers | 3 P + 1 B | 24 / 19 | 3 points | 14 or |
| 4 | L'étau | 4 P + 1 N + 1 B | 25 / 21 | 4 points | 16 or |
| 5 | Le bastion | 3 P + 1 R + 1 B | 26 / 23 | 5 points | 19 or |
| 6 | Le roi de fer | 3 P + 1 N + 1 R + 1 Q | 28 / 25 | 8 points | 24 or |

**Règle de victoire clarifiée** : capturer le Roi adverse **gagne immédiatement** même lors du dernier tick du joueur. Sinon, épuiser les ticks ennemis ne suffit plus à gagner « en attendant » : la mission de la manche doit avoir été accomplie en capturant au moins le nombre demandé de **points matériels non-roi** (P=1, N/B=3, R=5, Q=9, A=12). Le HUD affiche en temps réel le compteur capturé/requis. Si l'ennemi est à court de ticks sans objectif atteint, la mission est perdue ; si les ticks joueur finissent, la manche est perdue. Capturer son propre Roi adverse ou épuiser les ticks ont une priorité explicite pour éviter une victoire sur la même action où le Roi est capturé.

**Hypothèse produit à valider humainement** : l'objectif « captures OU Roi » favorise le combat actif, tout en conservant la course aux ticks spécifique au roguelite. Ce changement de règle est conséquent et ne doit pas être fusionné sans parties de test et validation de l'intention de game design.

### Trois voies sélectionnables entre chaque combat (boutique)

| Voie | Avantage | Coût/contrepartie | Intention |
| --- | --- | --- | --- |
| Équilibrée | Profil normal de la manche | Récompense de base | Référence |
| Prudente | +5 ticks joueur **et gel de la plus forte pièce ennemie au premier tour adverse** | −4 or sur la récompense en cas de victoire | Sûreté tactique contre progression plus lente |
| Audacieuse | +8 or sur la récompense en cas de victoire | +1 Cavalier ennemi, +3 ticks ennemis, +2 points d'objectif matériel | Récompense plus élevée contre défi réellement supérieur |

Le choix ne s'applique **qu'à la manche suivante**. Les données d'une manche terminée gardent la voie réellement choisie. La voie du premier combat est équilibrée. Aucun échange de pièces ou achat n'est annulé lors de la sélection. L'interface boutique affiche les budgets de ticks tenant déjà compte des achats effectués.

## 3. Fonctionnalités et fichiers livrés

- \`src/core/campaign.py\` : validation des six rencontres, voies et économies, plan de combat, récompenses, objectif de prises, offres de boutique et historique local borné.
- \`src/core/formation.py\` : placement commun aux deux camps ; tous les pions, renforts et achats sont visibles sur le plateau ou un état invalide est explicitement rejeté.
- \`content/shop_items.json\` : six formations et objectifs, nom, budgets et récompenses explicites.
- \`src/main.py\` : route de boutique, HUD de mission, récompense, remises à zéro au bon moment, conservation des achats, gel de la plus grosse menace en voie prudente, historique de la manche en fin de combat.
- \`tools/campaign_balance.py\` : tableau exact de composition, ticks, récompenses et objectifs ; option **facultative** \`--save chemin_vers_save.json\` pour analyser seulement les manches **réellement terminées par le joueur**, réparties par manche/voie/niveau d'IA, avec intervalle de Wilson 95 % indicatif.
- \`tools/autoplay_balance.py\` : 36 tests de sparring réel Board/AI niveau Facile (6 manches × 3 voies × 2 couleurs) **sans boutique, sans progression entre manches, sans pouvoirs de départ**. C'est un test de faisabilité des règles, non une simulation réaliste du joueur, ni un taux de victoire extrapolable.
- \`tests/test_campaign.py\`, \`tests/test_campaign_app.py\` et smoke \`tests/smoke_pygame.py\` : fonds de règles, achats, transitions, réglages, gel, mission, victoire et plusieurs corps d'armée, UI réelle via SDL simulé.
- \`.github/workflows/campaign.yml\` : Python 3.12, tests de tous les modules et Pygame avec vraies ressources, script de paramètres, sparring déterministe.

## 4. Paramètres économiques et raisons des choix

- Première manche : **22 ticks joueur, 16 ennemi**, au lieu de 100/100 accidentels. Chaque manche a ensuite une progression lisible plutôt qu'une chute de 100 à 14.
- Taux de récompense conservé à \`tick_reward_factor=0.06\` ; récompense de base augmente avec l'étape. La voie prudente sacrifie une partie des gains, l'audacieuse bénéficie d'un supplément uniquement sur victoire.
- Achat tick +10 : effectif sur le combat suivant et conservé pendant la transition.
- « −10 % ticks ennemi » : retire **10 % du budget ennemi du combat suivant**, arrondi vers le haut, au lieu de diminuer sa dépense par coup sur toutes les manches ; plafond cumulé de 35 % si futurs effets multiples.
- Double coup « prochaine manche » : consommé une fois, contrairement à « chaque manche » permanent pendant la run.
- Doubler l'or : bénéfice brut limité à +36 avant coût de 18, pour éviter une multiplication illimitée entre boutiques.
- Offres : **deux options abordables quand le catalogue en contient au moins deux**, sinon la seule disponible, avec une troisième option ouverte. L'applicabilité métier (cases libres pour l'achat d'une pièce) reste validée à l'achat ; les biais de couleur inutiles en cours de run ne sont plus proposés.
- Choix du niveau d'IA de la PR de base **conservé**. On ne réécrit pas l'expérience sous un réglage de difficulté caché.

Ces chiffres sont des **hypothèses initiales**, PAS « les bonnes valeurs » garanties. L'outil fournit les mesures pour les ajuster après retours humains et exécution de vraies runs.

## 5. Observer le vrai jeu sans collecte externe

Chaque manche **terminée** écrit un petit relevé anonyme dans \`campaign_balance_history\`, dans la sauvegarde locale existante : numéro, voie, niveau d'IA, victoire/défaite, ticks restants et matériel survivant. L'historique conserve uniquement les **200 derniers combats**, sans texte libre, pseudonyme ou accès réseau. **Les sorties de jeu non terminées ne sont pas enregistrées comme défaites**, donc biais de sélection à prendre en compte.

Analyse facultative depuis un environnement local, sans upload :

\`\`\`bash
python tools/campaign_balance.py
python tools/campaign_balance.py --save src/meta/save.json
\`\`\`

Pour un seul joueur, un taux observé (et même son intervalle Wilson) ne démontre pas un taux de réussite pour tous. Regrouper par niveau d'IA et par voie, puis par version du jeu, avant de tirer des conclusions. **Limite actuelle** : les logs ne contiennent pas encore le SHA de version du jeu et les abandons, à ajouter avant exploitation longitudinale sérieuse. Éviter de mélanger une version antérieure de campagne avec les nouvelles règles.

## 6. Passage de relais Codex, sans perturber les autres branches

Cette contribution de vraie fonctionnalité doit être revue **après la PR #2 (IA tactique)**, elle-même empilée sur **PR #1 (corrections boutique/échecs)**. Ne pas rebaser de force, ne pas fusionner une branche fille avant ses dépendances.

**Contrôles pré-merge indispensables** :
1. \`python -m unittest discover -s tests -p 'test_*.py' -v\` ; toutes les suites existantes et nouvelles.
2. \`SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=. python tests/smoke_pygame.py\` avec Pygame/Pillow réels.
3. Deux parties manuelles jusqu'au boss, l'une comme Blancs, l'autre comme Noirs, puis parties avec les trois voies et les trois niveaux d'IA.
4. Vérifier que les objectifs sont lisibles dans l'interface, que la voie prudente peut changer le résultat et que les trois cartes du magasin contiennent des achats pertinents/abordables.
5. Observer les vrais taux de victoire, captures, manque de ticks, récompenses, achats, temps par manche et abandons ; ajuster la campagne **sans masquer les échecs**.

**Faiblesses restantes connues et non revendiquées comme corrigées** : aucune validation humaine des six manches, pas de model de difficulté perceptuelle fiable, bouton boutique insuffisant pour certaines petites résolutions, impossibilité de reconduire une manche en cas d'interruption, pas d'autoplay avec achats ni métaprogression, achat de biais toujours listé dans le JSON source mais exclu de la boutique (à revoir lors d'une refonte de méta-économie).

## 7. Décision scientifique

Une IA simple gagnant/perdant contre elle-même ne suffit pas pour prétendre avoir trouvé « l'équilibrage pertinent ». La première expérience a invalidé notre ancienne règle de victoire automatique. Le nouveau protocole sert à **falsifier rapidement** les règles et instrumenter des vraies parties, non à faire passer une intuition pour un jeu fini. Codex doit valider le changement d'objectif de manche auprès du propriétaire avant toute intégration en production.
