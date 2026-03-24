from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme








# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'yellow-map'
    #game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 100  # frames per second
    game.mainiteration()
    player = game.player
    
def main():

    #for arg in sys.argv:
    #iterations = 40 # nb de pas max par episode
    #if len(sys.argv) == 2:
    #    iterations = int(sys.argv[1])
    #print ("Iterations: ")
    #print (iterations)

    init()
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nb_lignes = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize
    assert nb_lignes == nb_cols # a priori on souhaite un plateau carre
    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker le contour)
    lMax=nb_lignes-2
    cMin=2
    cMax=nb_cols-2
   
    
    players = [o for o in game.layers['joueur']]
    nb_players = len(players)
    


    items = [o for o in game.layers["ramassable"]]  #
    nb_fioles = len(items)

    nb_episodes = 100 #-AAAAAAAAAAAAAAAAAAAAAAAAaaa------------------


    #-------------------------------
    # Fonctions permettant de récupérer les listes des coordonnées
    # d'un ensemble d'objets ou de joueurs
    #-------------------------------

    def item_states(items):
        # donne la liste des coordonnees des items
        return [o.get_rowcol() for o in items]
    
    def player_states(players):
        # donne la liste des coordonnees des joueurs
        return [p.get_rowcol() for p in players]
    


    #-------------------------------
    # Rapport de ce qui est trouve sut la carte
    #-------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print('joueurs:', nb_players)
    print("fioles:",nb_fioles)
    print("lignes:", nb_lignes)
    print("colonnes:", nb_cols)
    print("-------------------------------------------")

    #-------------------------------
    # Carte demo yellow
    # 2 x 8 joueurs
    # 5 fioles jaunes
    #-------------------------------

    team = [[], []]  # 2 équipes
    for o in players:
        (x, y) = o.get_rowcol()
        if x == 2:  # les joueurs de team0 sur la ligne du haut
            team[0].append(o)
        elif x == 18:  # les joueurs de team1 sur la ligne du bas
            team[1].append(o)

    assert len(team[0]) == len(team[1])  # on veut un match équilibré donc équipe de même taille
    nb_players_team = int(nb_players / 2)

    init_states = [[],[]]
    # print(teamA)
    init_states[0] = player_states(team[0])

    # print(teamB)
    init_states[1] = player_states(team[1])


    #-------------------------------

    #-------------------------------
    # Fonctions definissant les positions legales et placement aléatoire
    #-------------------------------

    def around_pos(pos):
        # donne la liste des positions autour d'une pos (x,y) donnee
        x,y=pos
        return [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]

    def around_pos_free(pos):
        return [pos for pos in around_pos(pos) if legal_position(pos)]

    def busy(pos):
        return around_pos_free(pos) == []

    def legal_position(pos):
        row,col = pos
        # une position legale est dans la carte et pas sur une fiole ni sur un joueur
        return ((pos not in item_states(items)) and (pos not in player_states(players)) and row>lMin and row<lMax-1 and col>=cMin and col<cMax)

#-------------------------------Fonvtion ajoute ------------------------------------------------------------------------------

    def obtenir_toutes_allocations(joueurs_restants, fioles_restantes):
    # oblige de mettre le reste des joeour dans la derniere fiole
        if fioles_restantes == 1:
            return [[joueurs_restants]]
        
        allocations = []
        for i in range(joueurs_restants + 1):
            pour_cette_fiole = i
            pour_les_autres = obtenir_toutes_allocations(joueurs_restants - i, fioles_restantes - 1)
            for reste in pour_les_autres:
                allocations.append([pour_cette_fiole] + reste)
        return allocations

    def simuler_score_map(action, act_adv, regles_fioles, equipe_id):
        point_p1 = 0
        point_p2 = 0
        
        for i in range(len(regles_fioles)):
            if equipe_id == 0:
                x = action[i]
                y = act_adv[i]
            else:
                x = act_adv[i]
                y = action[i]

            regle = regles_fioles[i]

            if regle == "yellow":
                if x > y: 
                    point_p1 += 1
                elif x < y: 
                    point_p2 += 1

            elif regle == "red":
                if x > y: 
                    point_p1 += 1 if x >= 2 else 0
                elif x < y: 
                    point_p2 += 1 if y >= 2 else 0

            elif regle == "green":
                somme = x + y 
                if x > y: 
                    point_p1 += 1 if somme >= 3 else 0
                elif x < y: 
                    point_p2 += 1 if somme >= 3 else 0

            elif regle == "blue":
                if x > y:
                    if y == 1 : 
                        point_p2 += 1
                    elif x >= 2: 
                        point_p1 += 1
                if x < y:
                    if x == 1 : 
                        point_p1 += 1
                    elif y >= 2: 
                        point_p2 += 1
        
        # On renvoie les points obtenus par l'équipe qui est en train de réfléchir

        if equipe_id == 0:
            return point_p1
        else:
            return point_p2

#--------------------------------------------------------------------------------------------------------------------------

    def players_around_item(f):
        """
        :param f: objet fiole
        :return: nombre d'objet de chaque team
        """
        are_here = [0,0]
        pos = f.get_rowcol()
        for i in [0,1]:
            for j in team[i]:
                if j.get_rowcol() in around_pos(pos):
                    are_here[i]+=1
        return are_here

    def strategie_aleatoire(equipe_id, historique_perso, historique_adv, map_name):
    
        allocation = [0] * nb_fioles
        
        # Chaque joueur choisit une fiole au hasard
        for _ in range(nb_players_team):
            index_fiole_choisie = random.randint(0, nb_fioles - 1)
            allocation[index_fiole_choisie] += 1
            
        return allocation

    def strategie_tetu(equipe_id, historique_perso, historique_adv, map_name):
        # Si c'est le jour 1, on génère une allocation aléatoire qui debens fixe
        if len(historique_perso) == 0:
            return strategie_aleatoire(equipe_id, historique_perso, historique_adv, map_name)
        
        # Sinon, on rejoue strictement l'allocation du jour 1
        return historique_perso[0]

    
    def strategie_distribution(equipe_id, historique_perso, historique_adv, map_name):
        allocation = [0] * nb_fioles
        nb_fioles_remplit = nb_fioles - 2
        joueur_par_fiole = nb_players_team // nb_fioles_remplit
        joueurs_restants = nb_players_team % nb_fioles_remplit
        
        for i in range(nb_fioles_remplit):
            allocation[i] = joueur_par_fiole
            # On ajoute 1 joueur supplémentaire aux premières fioles jusqu'à épuisement du reste
            if i < joueurs_restants:
                allocation[i] += 1
                
        # On mélange la liste pour que les joueurs en plus ne soient pas toujours sur les fioles [0], [1] ect ...
        random.shuffle(allocation)
        
        return allocation


    def strategie_fictitious_play(equipe_id, historique_perso, historique_adv, map_name):
        # pasas d'historique, on joue une répartition par défaut
        if len(historique_adv) == 0:
            return strategie_distribution(equipe_id, historique_perso, historique_adv, map_name)

        meilleure_action = None
        meilleur_score = -1
        #puis on cherche la meilleur reponse face a l'historique_adv en cherchant dans tout les alloc possible
        for action in TOUTES_LES_ALLOCATIONS:
            score_espere = 0
            
            #on teste l'action contre TOUS les coups réels de l'historique adv et jee calcule l'espérance de victoire de mon action 
            for alloc_adverse in historique_adv:
                score_espere += simuler_score_map(action, alloc_adverse, regles_fioles, equipe_id)

            # On cherche l'action qui accumule le plus de victoires 
            if score_espere > meilleur_score:
                meilleur_score = score_espere
                meilleure_action = action

        return meilleure_action

    
    def strategie_regret_matching(equipe_id, historique_perso, historique_adv, map_name):
        #pas d'historique, on joue une répartition par défaut
        if len(historique_adv) == 0:
            return strategie_distribution(equipe_id, historique_perso, historique_adv, map_name)

        #le tableau des regrets pour les actions possibles
        regrets_cumules = [0.0] * len(TOUTES_LES_ALLOCATIONS)

        #rejouer le passé pour calculer le regret de chaque action
        for i in range(len(historique_adv)):
            adv_action = historique_adv[i]
            mon_action_reelle = historique_perso[i]
            
            #score qu'on a vraiment obtenu à ce tour
            score_reel = simuler_score_map(mon_action_reelle, adv_action, regles_fioles, equipe_id)

            #on calcul du regret pour chaque action possible
            for j in range(len(TOUTES_LES_ALLOCATIONS)):
                action_possible = TOUTES_LES_ALLOCATIONS[j]
                score_possible = simuler_score_map(action_possible, adv_action, regles_fioles, equipe_id)
                
                # Le regret c'est la diff entre ce qu'on aurait pu avoir et ce qu'on a eu
                regrets_cumules[j] += (score_possible - score_reel)

        # on garde les regrets positifs
        regrets_positifs = [max(0, r) for r in regrets_cumules]
        somme_regrets = sum(regrets_positifs)

        if somme_regrets > 0:
            #la probabilité de jouer une action est proportionnelle à son regret 
            probabilites = [r / somme_regrets for r in regrets_positifs]
            # np.random.choice choisit un index selon les probabilités fournies
            index_choisi = np.random.choice(len(TOUTES_LES_ALLOCATIONS), p=probabilites)
            return TOUTES_LES_ALLOCATIONS[index_choisi]
        else:
            # Si la somme est 0 (on a toujours joué le meilleur coup possible), on choisit au hasard
            index_choisi = random.randint(0, len(TOUTES_LES_ALLOCATIONS) - 1)
            return TOUTES_LES_ALLOCATIONS[index_choisi]

    

    
    
    def jouer_match(nom_map, strat_func0, strat_func1, mode_graphique=False):
        gagnant0 = 0
        gagnant1 = 0
        historique_t0 = []
        historique_t1 = []
        for e in range(nb_episodes):
            alloc_t0 = strat_func0(0, historique_t0, historique_t1, nom_map)
            alloc_t1 = strat_func1(1, historique_t1, historique_t0, nom_map)

            historique_t0.append(alloc_t0)
            historique_t1.append(alloc_t1)

            point_p1 = 0
            point_p2 = 0
            if mode_graphique == True:
                cibles_t0 = []
                cibles_t1 = []
                priorite = [0, 1] if e % 2 == 0 else [1, 0]

                for index_fiole in range(nb_fioles):
                    fiole = items[index_fiole]
                    pos_autour = around_pos(fiole.get_rowcol())
                    # on récupère les cases libres sur la carte
                    places_dispo = [pos for pos in pos_autour if legal_position(pos)]
                    random.shuffle(places_dispo) # on mélange comme ça on se place pas tjr au même endroit
                    #on recupere le nb de joueur par equipe, a envoyer a la fiole pour chaque tour dans la boucle suivant
                    demandes = {0: alloc_t0[index_fiole], 1: alloc_t1[index_fiole]} 
                    for eq in priorite:
                        nb_joueurs_envoyes = demandes[eq]
                        for _ in range(nb_joueurs_envoyes):
                            if len(places_dispo) > 0:
                                case_attribuee = places_dispo.pop(0)
                                if eq == 0: cibles_t0.append(case_attribuee)
                                else: cibles_t1.append(case_attribuee)
                            else:
                                # Si y'a pas de place autour de la fiole , le joueur n'a pas de place 
                                # donc on lui assigne None pour qu'il ne bouge pas
                                if eq == 0: cibles_t0.append(None)
                                else: cibles_t1.append(None)

                choix_pos_total = [cibles_t0, cibles_t1]
                chemins = [[], []]

                # -------------------------------
                # calcul A* pour le joueur
                # -------------------------------

                for t in [0, 1]:
                    for p in range(nb_players_team):
                        cible = choix_pos_total[t][p]
                        # Si le joueur n'a pas trouver de place devant la fiole , ilne bouge pas
                        if cible is None:
                            chemins[t].append([]) 
                            continue
                        
                        pos_player = team[t][p].get_rowcol()
                        g = np.ones((nb_lignes, nb_cols), dtype=bool)
                        for i in range(nb_lignes): # on exclut aussi les bordures du plateau
                            g[0][i] = False
                            g[1][i] = False
                            g[nb_lignes - 1][i] = False
                            g[nb_lignes - 2][i] = False
                            g[i][0] = False
                            g[i][1] = False
                            g[i][nb_lignes - 1] = False
                            g[i][nb_lignes - 2] = False
                        prob = ProblemeGrid2D(pos_player, cible, g, 'manhattan')
                        chemin = probleme.astar(prob, verbose=False)
                        chemins[t].append(chemin)

                #-------------------------------
                # Boucle principale de déplacements
                #-------------------------------
                # Maintenant que tous les itinéraires sont calculés, on fait bouger les sprites sur l'écran.
                # On intègre ici l'alternance de priorité pour l'équité de l'affichage.

                priority_move = [0, 1] if e % 2 == 0 else [1, 0]
                for t in priority_move:
                    for p in range(nb_players_team):
                        # Il faut toujours vérifier que le chemin a bien été trouvé
                        if chemins[t][p] is not None:
                            for i in range(len(chemins[t][p])):
                                (row, col) = chemins[t][p][i]
                                team[t][p].set_rowcol(row, col)
                                # On met à jour l'affichage à chaque pas
                                game.mainiteration()

                # -------------------------------
                # Calcul des scores
                # ------------------------------
                for i_fiole in range(nb_fioles):
                    o = items[i_fiole]
                    x, y = players_around_item(o)
                    regle = regles_fioles[i_fiole] # On récupère la règle de cette fiole 

                    if regle == "yellow":
                        if x > y: 
                            point_p1 += 1
                        elif x < y: 
                            point_p2 += 1
                    elif regle == "red":
                        if x > y: 
                            point_p1 += 1 if x >= 2 else 0
                        elif x < y: 
                            point_p2 += 1 if y >= 2 else 0
                    elif regle == "green":
                        somme = x+y 
                        if x > y: 
                            point_p1 += 1 if somme >= 3 else 0
                        elif x < y: 
                            point_p2 += 1 if somme >= 3 else 0
                    elif regle == "blue":
                        if x > y:
                            if y==1: 
                                point_p2 += 1
                            elif x >= 2: 
                                point_p1 += 1
                        if x < y:
                            if x == 1: 
                                point_p1 += 1
                            elif y >= 2: 
                                point_p2 += 1
                print("le nombre de point obtenue par le joeur 0 est ", point_p1,
                " et par le joeur 1 est", point_p2)

                gagnant = -1
                
                if point_p1 > point_p2:
                    gagnant = 0
                elif point_p1 < point_p2:
                    gagnant = 1
                if gagnant != -1:
                    print("le joeur gagnat est", gagnant)
                else:
                    print("on a un match null ")

                # remettre les joueurs à leur pos initiale a la fin de l'episode
                for i in [0,1]:
                    j=0
                    for p in team[i]:
                        x,y = init_states[i][j]
                        p.set_rowcol(x,y)
                        j+=1

            else:
                # --- mode sans graphisme ---
                point_p1 = simuler_score_map(alloc_t0, alloc_t1, regles_fioles, 0)
                point_p2 = simuler_score_map(alloc_t1, alloc_t0, regles_fioles, 1)

            
            if point_p1 > point_p2: gagnant0 += 1
            elif point_p1 < point_p2: gagnant1 += 1

        return gagnant0, gagnant1


    # -------------------------------
    # Tournoi
    # -------------------------------
    
    cartes_a_tester = ["yellow-map", "red-map", "green-map", "blue-map", "mixed-map"]
    
    strategies = [
        ("Aleatoire", strategie_aleatoire),
        ("Tetu", strategie_tetu),
        ("Distribution", strategie_distribution),
        ("Fictitious", strategie_fictitious_play),
        ("RegretMatch", strategie_regret_matching)
    ]

    resultats_finaux = []

    #
    # on dé-commente ces lignes si on veux juste observer un match visuellement.
    TOUTES_LES_ALLOCATIONS = obtenir_toutes_allocations(nb_players_team, nb_fioles)
    regles_fioles = ["yellow"] * nb_fioles
    score0, score1 = jouer_match("yello-map", strategie_fictitious_play, strategie_regret_matching, mode_graphique=True)
    sys.exit()
    pygame.quit()

    # lancement du Tournoi 
    for map_actuelle in cartes_a_tester:
        print(f"\n--- MATCHS SUR {map_actuelle.upper()} ---")


        init(map_actuelle)
        items = [o for o in game.layers["ramassable"]]
        nb_fioles = len(items)
        players = [o for o in game.layers['joueur']]
        nb_players = len(players)
        nb_players_par_team = int(nb_players / 2)
        TOUTES_LES_ALLOCATIONS = obtenir_toutes_allocations(nb_players_par_team, nb_fioles)

        #on extrait la règle par fiole depuis le JSON
        regles_fioles = []
        donnees_json_fioles = []
        largeur_carte = game.spriteBuilder.colsize
        #on recupere la partie data  de ramassable dans le json de la map 
        for layer in game.spriteBuilder.carte["layers"]:
            if layer["name"] in ["ramassables"]:
                donnees_json_fioles = layer["data"]
                break
                    
        #on va chercher la rule de chaque fioles 
        for o in items:
            row, col = o.get_rowcol()
            index_liste = (row * largeur_carte) + col 
            numero_fiole = donnees_json_fioles[index_liste]
            
            #on identifie la ruel 
            
            if "yellow" in map_actuelle or numero_fiole == 306: 
                rule = "yellow"
            elif "red" in map_actuelle or numero_fiole == 277: 
                rule = "red"
            elif "green" in map_actuelle or numero_fiole == 338: 
                rule = "green" #le or c'est parceque y'a une difference entre le numero utilise dans la green map et dans la mixed map 
            elif "blue" in map_actuelle or numero_fiole == 293: 
                rule = "blue"
            
            regles_fioles.append(rule)

        for i in range(len(strategies)):
            for j in range(i + 1, len(strategies)):
                nom0, func0 = strategies[i]
                nom1, func1 = strategies[j]
                
                # on execute sans le graphisme pour que s'aille vite 
                score0, score1 = jouer_match(map_actuelle, func0, func1, mode_graphique=False) 
                
                resultats_finaux.append(f"[{map_actuelle}] {nom0:<12} ({score0}) - ({score1}) {nom1}")
                print(f"[{map_actuelle}] {nom0} ({score0}) - ({score1}) {nom1}")

    # Résumé
    print("\n\n" + "="*50)
    print("RÉSUMÉ ")
    print("="*50)
    for ligne in resultats_finaux:
        print(ligne)

    pygame.quit()


    
    #-------------------------------

    
   

if __name__ == '__main__':
    main()
    


