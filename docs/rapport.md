# Rapport de projet

## Groupe
* Sedira mohammed 

## Description des choix importants d'implémentation

# 1 la gestion de la mixed-map
Pour gérer la carte mixed-map (qui mélange les couleurs), j'ai regardé comment le fichier JSON est construit. J'ai remarqué que dans la partie ramassables, le tableau data utilise des numéros précis pour chaque fiole (306 pour jaune, 293 pour bleu, etc.). Mon code calcule l'index (ligne, colonne) de chaque objet sur la carte et va lire ce numéro directement dans la liste data. c'est comme ça que mon code connaît automatiquement la couleur et la règle de chaque fiole.

# 2. simuler_score_map
la premiere version de cette fonction prenait en compte uniqueement le nom de la map 
pour calculer les des equipeq, quand j'ai introduit la mixed-map j'ai ajuster la fonction en ajoutant une liste regles_fioles qui contient la couleur de chaque fiole
maintenant le simulateur calcule les points fiole par fiole, en appliquant la bonne règle (rouge, vert, etc.) pour chacune d'entre elles.

# 3. Génération automatique des choix (obtenir_toutes_allocations)
J'ai créé la fonction obtenir_toutes_allocations pour calculer dynamiquement toutes les combinaisons possible de distribution de joueur sur les fioles. L'IA possède donc toujours la liste exacte de ses choix possibles, quelle que soit la carte chargée.



# 5. L'arbitre 
En semaine 1, les joueurs jouaient chacun leur tour et donc quand un joueur veut jouer , il verifie que il ne y'a pas de joueur a cote de la fiole et il joue . Mais dans la semaine 2, le calcul de strategies impose que les équipes prennent leurs décisions en même temps. Pour régler ça, j'ai mis en place un système d'arbitre. Les deux stratégies donnent leur allocation globale en même temps. L'arbitre regarde les places disponibles autour des fioles, mélange ces places (pour ne pas ne pas se placer toujour au meme endroit), et les distribue équitablement aux joueurs envoyés. Pour que ce soit 100% juste, l'arbitre alterne l'équipe prioritaire à chaque nouveau tour. Une fois les cibles données, tous les joueurs calculent leur chemin (A*) et se déplacent en même temps.

## Description des stratégies proposées

# 1. Stratégie Aléatoire 
À chaque tour, elle distribue les joueurs au hasard parmi les fioles disponibles. Elle ne prend en compte  l'historique de l'adversaire.

# 2. Stratégie Têtu
Au premier tour, cette stratégie génère une répartition aléatoire de ses joueurs grace a la strategie aleatoire. Pour tous les tours suivants, elle rejoue cette même répartition..

# 3. Stratégie Distribution
Il s'agit d'une stratégie arbitraire fixe. Elle sélectionne (nb_fioles - 2)  sur la carte et y concentre ses forces selon une distribution plus au moins uniforme des joueur. Les autres fioles sont laissées vides.

# 4. Stratégie Fictitious Play 
le Fictitious Play est défini par le fait de jouer la meilleure réponse face à l'historique joué par l'adversair
À chaque tour, elle parcourt tout l'historique des actions adverses. Pour chacune des actions possibles, elle utilise simule_score_map pour calculer quel serait son "score espéré" contre cet historique. Elle choisit ensuite l'action qui accumule la meilleure espérance. Elle trouve la faille contre des stratégies rigides comme Têtu ou Distribution.

# 5. Stratégie Regret Matching 
Cette stratégie se base sur la question: "Aurais-je eu un meilleur score si j'avais joué autre chose dans le passé ?".
À chaque tour, elle rejoue virtuellement tout l'historique du match. Pour chaque action possible, elle calcule la différence entre les points qu'elle aurait pu marquer et les points qu'elle a réellement marqués. Si cette différence est positive, c'est un "regret". Pour choisir son prochain coup, l'algorithme tire une action au hasard, mais en donnant une probabilité beaucoup plus forte aux actions qui ont accumulé beaucoup de regret. Cela lui permet de s'adapter dynamiquement aux adversaires qui changent souvent de tactique.
Le choix au hasard de la prochaine action :
si je choisi toujours l'action avec le regret maximum, il devient 100% prévisible. Un adversaire intelligent va analyser mon historique, comprendre ma faille, deviner mon prochain coup. En utilisant des probabilités, je favorise mes meilleurs coups tout en gardant une part de hasard pour empêcher l'adversaire de me contrer.

## Description des résultats
Comparaison entre les stratégies. Bien indiquer les cartes utilisées.

## RÉSUMÉ 

[yellow-map] Aleatoire    (48) - (11) Tetu

[yellow-map] Aleatoire    (16) - (25) Distribution

[yellow-map] Aleatoire    (21) - (32) Fictitious

[yellow-map] Aleatoire    (24) - (32) RegretMatch

[yellow-map] Tetu         (17) - (34) Distribution

[yellow-map] Tetu         (0) - (99) Fictitious

[yellow-map] Tetu         (0) - (99) RegretMatch

[yellow-map] Distribution (46) - (53) Fictitious

[yellow-map] Distribution (37) - (50) RegretMatch

[yellow-map] Fictitious   (46) - (46) RegretMatch

[red-map] Aleatoire    (13) - (32) Tetu

[red-map] Aleatoire    (3) - (69) Distribution

[red-map] Aleatoire    (3) - (63) Fictitious

[red-map] Aleatoire    (6) - (62) RegretMatch

[red-map] Tetu         (0) - (61) Distribution

[red-map] Tetu         (0) - (100) Fictitious

[red-map] Tetu         (0) - (99) RegretMatch

[red-map] Distribution (16) - (24) Fictitious

[red-map] Distribution (14) - (28) RegretMatch

[red-map] Fictitious   (34) - (60) RegretMatch

[green-map] Aleatoire    (5) - (69) Tetu

[green-map] Aleatoire    (49) - (19) Distribution

[green-map] Aleatoire    (1) - (93) Fictitious

[green-map] Aleatoire    (0) - (94) RegretMatch

[green-map] Tetu         (95) - (0) Distribution

[green-map] Tetu         (1) - (99) Fictitious

[green-map] Tetu         (0) - (100) RegretMatch

[green-map] Distribution (1) - (99) Fictitious

[green-map] Distribution (1) - (99) RegretMatch

[green-map] Fictitious   (7) - (14) RegretMatch

[blue-map] Aleatoire    (59) - (30) Tetu

[blue-map] Aleatoire    (32) - (47) Distribution

[blue-map] Aleatoire    (23) - (61) Fictitious

[blue-map] Aleatoire    (29) - (50) RegretMatch

[blue-map] Tetu         (25) - (75) Distribution

[blue-map] Tetu         (0) - (100) Fictitious

[blue-map] Tetu         (0) - (100) RegretMatch

[blue-map] Distribution (11) - (86) Fictitious

[blue-map] Distribution (34) - (46) RegretMatch

[blue-map] 66   (24) - (55) RegretMatch

[mixed-map] Aleatoire    (27) - (23) Tetu

[mixed-map] Aleatoire    (38) - (35) Distribution

[mixed-map] Aleatoire    (1) - (92) Fictitious

[mixed-map] Aleatoire    (7) - (62) RegretMatch

[mixed-map] Tetu         (100) - (0) Distribution

[mixed-map] Tetu         (0) - (100) Fictitious

[mixed-map] Tetu         (0) - (100) RegretMatch

[mixed-map] Distribution (0) - (98) Fictitious
[mixed-map] Distribution (0) - (99) RegretMatch
[mixed-map] Fictitious   (50) - (16) RegretMatch
