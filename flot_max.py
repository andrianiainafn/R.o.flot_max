def firstStep(graph):
    initGraph = {}
    for node in graph:
        initGraph[node] = [(edge[0], 0) for edge in graph[node]]
    return initGraph


def makeTable(graph):
    nodes = list(graph.keys())
    table = {}

    for node in graph:
        for edge, distance in graph[node]:
            key = f"{node}-{edge}"
            table[key] = [distance] + [0] * len(nodes)

    return table


def find_source_and_sink(graph):
    """
    Trouve automatiquement le noeud source et le noeud sink du graphe.
    Source: noeud qui n'est destination d'aucun arc
    Sink: noeud qui n'a pas d'arcs sortants
    """
    all_nodes = set(graph.keys())
    destinations = set()

    # Collecter tous les noeuds de destination
    for node in graph:
        for dest, _ in graph[node]:
            destinations.add(dest)
            all_nodes.add(dest)

    # Source: noeud qui n'est jamais une destination
    sources = all_nodes - destinations

    # Sink: noeud qui n'a pas d'arcs sortants (pas dans les clés du graphe)
    sinks = destinations - set(graph.keys())

    # Prendre le premier source et sink trouvés
    source = list(sources)[0] if sources else None
    sink = list(sinks)[0] if sinks else None

    return source, sink


def constructGraph(t, graph):
    """
    Construit le graphe en mettant à jour ses arcs et la table de façon itérative.
    Priorité au chemin le plus court contenant l'arc minimum.

    Args:
        t (dict): La table des arcs
        graph (dict): Le graphe initial

    Returns:
        tuple: (graphe mis à jour, table mise à jour)
    """
    # CHANGEMENT 1: Trouver automatiquement source et sink
    source, sink = find_source_and_sink(graph)
    print(f"Source détectée: {source}, Sink détecté: {sink}")

    graphe_maj = graph.copy()
    premiere_cle, premiere_valeur = next(iter(t.items()))
    end = True
    n = 0

    while end:
        # Initialiser minim à la première valeur de la colonne n
        minim = premiere_valeur[n]
        if minim in ["S", "B"]:
            minim = float('inf')
        else:
            minim = float(minim)

        arc, minim = getMinimArc(t, n, minim)
        print(f"Itération {n + 1}, Arc sélectionné: {arc}, Valeur minimale: {minim}")

        # CHANGEMENT 2: Passer source et sink à la fonction
        graphe_maj, arcs_modifies = mettre_a_jour_arc(graphe_maj, arc[0], arc[1], minim, t, source, sink)
        print(f"Arcs modifiés: {arcs_modifies}")

        # Mettre à jour la table avec les nouvelles valeurs
        t = mettre_a_jour_table(t, n + 1, minim, graphe_maj, arcs_modifies, arc, source, sink)

        # Afficher l'état actuel du graphe et de la table
        print(f"Table après itération {n + 1}:", {k: v[:n + 2] for k, v in t.items()})
        print(f"Graphe après itération {n + 1}:", graphe_maj)
        n = n + 1
        end = verifier_valeurs_non_terminales(t)

    return graphe_maj, t


def getMinimArc(t, n, startMinim):
    """
    Trouve l'arc avec la valeur minimale dans la colonne n de la table.
    """
    print(startMinim)
    minim = startMinim if startMinim != 0 else float('inf')
    minim_key = ""

    for key, value in t.items():
        if n < len(value) and value[n] not in ["S", "B"] and isinstance(value[n], (int, float)):
            current_val = float(value[n])
            if current_val <= minim:
                minim = current_val
                minim_key = key

    if minim_key:
        arc = minim_key.split("-")
        return arc, minim
    else:
        return None, float('inf')


def mettre_a_jour_table(t, index, minim, graph, arcs_modifies, arcs, source, sink):
    a_verifier = "-".join(arcs)
    print("arc", a_verifier)
    # CHANGEMENT 3: Passer source et sink
    blocked = check_if_blocked(a_verifier, t, graph, source, sink)
    print("bloquer", blocked)

    for key, value in t.items():
        while len(value) <= index:
            value.append(value[index - 1])

    if blocked:
        # Si l'arc est bloqué, marquer toutes les colonnes restantes comme 'B'
        for i in range(index, len(t[a_verifier])):
            t[a_verifier][i] = 'B'
        print("arc modifiers quand blocked", arcs_modifies)
        print("blocked-arcs", t[a_verifier])

        # Pour tous les autres arcs, conserver la valeur précédente
        for key, value in t.items():
            if key != a_verifier:
                if index > 0 and (value[index - 1] == "S" or value[index - 1] == "B"):
                    continue
                else:
                    print("index, value", index, value)
                    value[index] = value[index - 1]
    else:
        for key, value in t.items():
            # Ignorer les entrées déjà marquées comme 'S' ou 'B'
            if index > 0 and (value[index - 1] == "S" or value[index - 1] == "B"):
                print("value: ", value)
                value[index] = value[index - 1]
                continue

            # Si l'arc est dans la liste des arcs modifiés
            if key in arcs_modifies:
                # Calculer la nouvelle valeur
                nouvelle_valeur = value[index - 1] - minim
                value[index] = nouvelle_valeur

                # Si la nouvelle valeur est 0, marquer comme 'S' (saturé)
                if nouvelle_valeur == 0:
                    for i in range(index, len(value)):
                        value[i] = 'S'
                    print(f"Arc {key} saturé: {value}")
            else:
                # Si l'arc n'est pas modifié, conserver la même valeur
                value[index] = value[index - 1]

    return t


def check_if_blocked(arc_requis, table, graph, source, sink):
    # CHANGEMENT 4: Passer source et sink
    chemin_plus_court = trouver_chemin_plus_court_avec_arc(graph, arc_requis, source, sink)

    if not chemin_plus_court:
        return True

    # Vérifier si le chemin le plus court est bloqué
    chemin_bloque = False
    for depart, arrivee in chemin_plus_court:
        if f"{depart}-{arrivee}" == arc_requis:
            continue

        arc_key = f"{depart}-{arrivee}"
        if arc_key in table:
            valeurs = table[arc_key]
            derniere_valeur = None
            for val in valeurs:
                if val not in [0, "0"] and val not in ["S", "B"]:
                    derniere_valeur = val
                elif val in ["S", "B"]:
                    derniere_valeur = val
                    break

            if derniere_valeur in ["S", "B"]:
                chemin_bloque = True
                break

    # Si le chemin le plus court est bloqué, vérifier les autres chemins
    if chemin_bloque:
        # CHANGEMENT 5: Passer source et sink
        tous_chemins = trouver_chemins_avec_arc(graph, arc_requis, source, sink)
        tous_bloques = True

        for chemin in tous_chemins:
            if chemin == chemin_plus_court:
                continue

            chemin_valide = True
            for depart, arrivee in chemin:
                if f"{depart}-{arrivee}" == arc_requis:
                    continue

                arc_key = f"{depart}-{arrivee}"
                if arc_key in table:
                    valeurs = table[arc_key]
                    derniere_valeur = None
                    for val in valeurs:
                        if val not in [0, "0"] and val not in ["S", "B"]:
                            derniere_valeur = val
                        elif val in ["S", "B"]:
                            derniere_valeur = val
                            break

                    if derniere_valeur in ["S", "B"]:
                        chemin_valide = False
                        break

            if chemin_valide:
                tous_bloques = False
                break

        return tous_bloques

    return False


def verifier_valeurs_non_terminales(table):
    """
    Vérifie s'il existe au moins un élément de la table qui n'a PAS une valeur 'B' ou 'S'
    à son dernier index.
    """
    for cle, liste in table.items():
        if not liste:
            return True

        derniere_valeur = liste[-1]
        if derniere_valeur != 'B' and derniere_valeur != 'S':
            return True

    return False


def mettre_a_jour_arc(graphe, depart, arrivee, valeur, table=None, source=None, sink=None):
    """
    Met à jour les arcs du graphe en prioritisant le chemin le plus court.
    Si le chemin le plus court est bloqué/saturé, utilise les autres chemins.
    """
    # CHANGEMENT 6: Détecter automatiquement si source et sink ne sont pas fournis
    if source is None or sink is None:
        source, sink = find_source_and_sink(graphe)

    arc_requis = f"{depart}-{arrivee}"

    # CHANGEMENT 7: Passer source et sink
    chemin_plus_court = trouver_chemin_plus_court_avec_arc(graphe, arc_requis, source, sink)
    print(f"Chemin le plus court pour {arc_requis}:", chemin_plus_court)

    chemins_a_utiliser = []

    if chemin_plus_court:
        # Vérifier si le chemin le plus court est valide
        chemin_valide = True
        if table:
            for source_arc, destination in chemin_plus_court:
                arc_key = f"{source_arc}-{destination}"
                if arc_key in table and arc_key != arc_requis:
                    for val in table[arc_key]:
                        if val in ["S", "B"]:
                            chemin_valide = False
                            print(f"Chemin le plus court bloqué à l'arc {arc_key}")
                            break
                if not chemin_valide:
                    break

        if chemin_valide:
            chemins_a_utiliser.append(chemin_plus_court)
            print(f"Utilisation du chemin le plus court: {chemin_plus_court}")
        else:
            # Si le chemin le plus court est bloqué, récupérer tous les autres chemins valides
            print("Chemin le plus court bloqué, recherche d'autres chemins...")
            # CHANGEMENT 8: Passer source et sink
            tous_chemins = trouver_chemins_avec_arc(graphe, arc_requis, source, sink)

            for chemin in tous_chemins:
                if chemin == chemin_plus_court:
                    continue

                chemin_valide = True
                if table:
                    for source_arc, destination in chemin:
                        arc_key = f"{source_arc}-{destination}"
                        if arc_key in table and arc_key != arc_requis:
                            for val in table[arc_key]:
                                if val in ["S", "B"]:
                                    chemin_valide = False
                                    break
                        if not chemin_valide:
                            break

                if chemin_valide:
                    chemins_a_utiliser.append(chemin)

    print(f"Chemins à utiliser pour {arc_requis}:", chemins_a_utiliser)

    # Mettre à jour seulement les arcs des chemins sélectionnés
    for chemin in chemins_a_utiliser:
        for source_arc, destination in chemin:
            if source_arc in graphe:
                for j, (dest, poids) in enumerate(graphe[source_arc]):
                    if dest == destination:
                        graphe[source_arc][j] = (dest, poids + valeur)
                        print(f"Mise à jour de l'arc {source_arc}-{destination}: {poids} -> {poids + valeur}")
                        break

    # Convertir en liste d'arcs modifiés
    arcs_modifies = [f"{source_arc}-{destination}" for chemin in chemins_a_utiliser for source_arc, destination in
                     chemin]
    arcs_modifies = list(set(arcs_modifies))

    return graphe, arcs_modifies


def trouver_chemin_plus_court_avec_arc(graph, arc_requis, source, sink):
    """
    Trouve le chemin le plus court (en nombre d'arcs) qui contient l'arc requis.
    """
    # CHANGEMENT 9: Utiliser les paramètres source et sink
    tous_chemins = trouver_chemins_avec_arc(graph, arc_requis, source, sink)

    if not tous_chemins:
        return None

    # Trouver le chemin avec le moins d'arcs
    chemin_plus_court = min(tous_chemins, key=len)
    return chemin_plus_court


def trouver_chemins_avec_arc(graph, arc_requis, source, sink):
    """
    Trouve tous les chemins qui contiennent l'arc requis.
    """
    if isinstance(arc_requis, str):
        debut, fin = arc_requis.split("-")
    else:
        debut, fin = arc_requis

    # Trouver tous les chemins de source à début
    chemins_vers_debut = []

    def dfs_vers_debut(noeud_courant, chemin_courant):
        if noeud_courant == debut:
            chemins_vers_debut.append(list(chemin_courant))
            return

        for voisin, poids in graph.get(noeud_courant, []):
            if not any(arc[0] == voisin for arc in chemin_courant):
                chemin_courant.append((noeud_courant, voisin))
                dfs_vers_debut(voisin, chemin_courant)
                chemin_courant.pop()

    # CHANGEMENT 10: Utiliser le paramètre source
    dfs_vers_debut(source, [])

    # Trouver tous les chemins de fin à sink
    chemins_vers_omega = []

    def dfs_vers_omega(noeud_courant, chemin_courant):
        # CHANGEMENT 11: Utiliser le paramètre sink
        if noeud_courant == sink:
            chemins_vers_omega.append(list(chemin_courant))
            return

        for voisin, poids in graph.get(noeud_courant, []):
            if not any(arc[0] == voisin for arc in chemin_courant):
                chemin_courant.append((noeud_courant, voisin))
                dfs_vers_omega(voisin, chemin_courant)
                chemin_courant.pop()

    dfs_vers_omega(fin, [])

    # Combiner les chemins pour obtenir les chemins complets
    chemins_complets = []

    for chemin_debut in chemins_vers_debut:
        for chemin_fin in chemins_vers_omega:
            chemin_complet = list(chemin_debut)
            chemin_complet.append((debut, fin))
            chemin_complet.extend(chemin_fin)
            chemins_complets.append(chemin_complet)

    return chemins_complets


def maximiser_flot_final(graphe_final, table_finale, source, sink):
    """
    Implémente l'algorithme de Ford-Fulkerson avec marquage + et -.
    
    Règles :
    - On peut avancer sur les arcs marqués saturés (S)
    - On peut reculer sur les arcs marqués bloqués (B) qui ont du flot
    - On prend le minimum des capacités du chemin augmentant
    - On ajoute cette valeur aux arcs saturés et on la retire des arcs bloqués
    """
    print(f"\n=== DÉBUT DE LA MAXIMISATION DU FLOT ===")
    print(f"Source: {source}, Sink: {sink}")

    # Créer une copie du graphe pour travailler dessus
    graphe_courant = copier_graphe(graphe_final)
    flot_total = 0
    iteration = 1
    historique_chemins = []

    while True:
        print(f"\n--- Itération {iteration} ---")

        # Trouver un chemin augmentant avec marquage + et -
        chemin_augmentant = trouver_chemin_augmentant_ameliorer(graphe_courant, table_finale, source, sink)

        if not chemin_augmentant:
            print("Aucun chemin augmentant trouvé. Algorithme terminé.")
            break

        print(f"Chemin augmentant trouvé: {chemin_augmentant}")
        
        # Calculer la capacité minimale du chemin
        capacite_min = calculer_capacite_minimale_ameliorer(chemin_augmentant, graphe_courant, table_finale)
        print(f"Capacité minimale du chemin: {capacite_min}")
        
        if capacite_min <= 0:
            print("Capacité minimale nulle ou négative. Arrêt de l'algorithme.")
            break
        
        # Mettre à jour le graphe et la table
        graphe_courant, table_finale = mettre_a_jour_flot_et_table(graphe_courant, table_finale, chemin_augmentant, capacite_min)
        
        # Ajouter au flot total
        flot_total += capacite_min
        
        # Sauvegarder l'historique
        historique_chemins.append({
            'iteration': iteration,
            'chemin': chemin_augmentant,
            'capacite': capacite_min,
            'flot_cumule': flot_total
        })
        
        print(f"Flot ajouté: {capacite_min}")
        print(f"Flot total: {flot_total}")
        print(f"État du graphe après mise à jour:")
        afficher_graphe(graphe_courant)

        iteration += 1

    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"Flot maximal: {flot_total}")
    print(f"Nombre d'itérations: {iteration - 1}")
    
    return graphe_courant, flot_total, historique_chemins


def trouver_chemin_augmentant_ameliorer(graphe, table, source, sink):
    """
    Trouve un chemin augmentant en utilisant le marquage + et -.
    
    Règles de marquage :
    - Marquage + : on peut avancer sur les arcs saturés (S)
    - Marquage - : on peut reculer sur les arcs bloqués (B) qui ont du flot
    
    Returns:
        list: Liste de tuples (nœud_départ, nœud_arrivée, action) où action est '+' ou '-'
    """
    print(f"\nRecherche d'un chemin augmentant de {source} vers {sink}...")
    
    # Dictionnaire pour stocker les marquages des nœuds
    marquages = {}  # {noeud: (precedent, signe, capacite_min)}
    
    # File pour le parcours (BFS modifié)
    file = [(source, None, '+', float('inf'), [])]  # (nœud, precedent, signe, capacite_min, chemin)
    marquages[source] = (None, '+', float('inf'))
    
    print(f"Marquage initial: {source} -> +")
    
    while file:
        noeud_courant, precedent, signe_courant, capacite_min, chemin = file.pop(0)
        
        # Si on a atteint le sink, on a trouvé un chemin augmentant
        if noeud_courant == sink:
            print(f"Chemin augmentant trouvé jusqu'au sink!")
            return chemin
        
        # Explorer les voisins selon les règles de marquage
        if signe_courant == '+':
            # Avec +, on peut avancer sur les arcs saturés (S)
            voisins_satures = explorer_arcs_satures_ameliorer(noeud_courant, graphe, table)
            for voisin, capacite in voisins_satures:
                if voisin not in marquages:
                    nouvelle_capacite = min(capacite_min, capacite)
                    nouveau_chemin = chemin + [(noeud_courant, voisin, '+')]
                    file.append((voisin, noeud_courant, '+', nouvelle_capacite, nouveau_chemin))
                    marquages[voisin] = (noeud_courant, '+', nouvelle_capacite)
                    print(f"Marquage: {voisin} -> + (arc saturé depuis {noeud_courant}, capacité: {capacite})")
        
        # Explorer les arcs de retour (pour les arcs bloqués avec flot)
        voisins_retour = explorer_arcs_retour_ameliorer(noeud_courant, graphe, table)
        for voisin, flot_actuel in voisins_retour:
            if voisin not in marquages:
                nouvelle_capacite = min(capacite_min, flot_actuel)
                nouveau_chemin = chemin + [(noeud_courant, voisin, '-')]
                file.append((voisin, noeud_courant, '-', nouvelle_capacite, nouveau_chemin))
                marquages[voisin] = (noeud_courant, '-', nouvelle_capacite)
                print(f"Marquage: {voisin} -> - (retour depuis {noeud_courant}, flot: {flot_actuel})")
    
    print("Aucun chemin augmentant trouvé")
    return None


def explorer_arcs_satures_ameliorer(noeud, graphe, table):
    """
    Trouve tous les nœuds accessibles via des arcs saturés (S) depuis le nœud donné.
    Returns: liste de tuples (voisin, capacite_residuelle)
    """
    voisins = []
    
    # Chercher tous les arcs qui partent du nœud courant et qui sont saturés
    if noeud in graphe:
        for voisin, capacite in graphe[noeud]:
            arc_key = f"{noeud}-{voisin}"
            if arc_key in table:
                derniere_valeur = table[arc_key][-1] if table[arc_key] else None
                if derniere_valeur == 'S':
                    # Pour un arc saturé, la capacité résiduelle est la capacité actuelle du graphe
                    voisins.append((voisin, capacite))
    
    return voisins


def explorer_arcs_retour_ameliorer(noeud, graphe, table):
    """
    Trouve tous les nœuds accessibles via des arcs de retour (arcs bloqués avec flot).
    Returns: liste de tuples (voisin, flot_actuel)
    """
    voisins = []
    
    # Chercher tous les arcs qui arrivent au nœud courant et qui sont bloqués avec du flot
    for cle, valeurs in table.items():
        if '-' in cle:
            depart, arrivee = cle.split('-')
            if arrivee == noeud:
                # Vérifier si l'arc est bloqué (B)
                derniere_valeur = valeurs[-1] if valeurs else None
                if derniere_valeur == 'B':
                    # Chercher le flot actuel dans le graphe
                    if depart in graphe:
                        for voisin, capacite in graphe[depart]:
                            if voisin == arrivee:
                                # Le flot actuel est la capacité originale moins la capacité résiduelle
                                capacite_originale = None
                                for val in valeurs:
                                    if isinstance(val, (int, float)) and val > 0:
                                        capacite_originale = val
                                        break
                                
                                if capacite_originale:
                                    flot_actuel = capacite_originale - capacite
                                    if flot_actuel > 0:
                                        voisins.append((depart, flot_actuel))
                                break
    
    # Chercher aussi les arcs de retour dans le graphe résiduel
    if noeud in graphe:
        for voisin, capacite in graphe[noeud]:
            # Si il y a un arc de retour avec capacité > 0, on peut l'utiliser
            if capacite > 0:
                voisins.append((voisin, capacite))
    
    return voisins


def calculer_capacite_minimale_ameliorer(chemin, graphe, table):
    """
    Calcule la capacité minimale d'un chemin augmentant.
    """
    capacites = []
    
    for arc_info in chemin:
        if len(arc_info) == 3:
            depart, arrivee, action = arc_info
        else:
            depart, arrivee = arc_info
            action = '+'
        
        if action == '+':
            # Pour les arcs d'avancement (saturés), prendre la capacité résiduelle
            if depart in graphe:
                for voisin, capacite in graphe[depart]:
                    if voisin == arrivee:
                        capacites.append(capacite)
                        break
        elif action == '-':
            # Pour les arcs de retour (bloqués), prendre le flot actuel
            arc_key = f"{depart}-{arrivee}"
            if arc_key in table:
                valeurs = table[arc_key]
                capacite_originale = None
                for val in valeurs:
                    if isinstance(val, (int, float)) and val > 0:
                        capacite_originale = val
                        break

                if capacite_originale:
                    # Chercher la capacité résiduelle actuelle
                    capacite_residuelle = 0
                    if depart in graphe:
                        for voisin, cap in graphe[depart]:
                            if voisin == arrivee:
                                capacite_residuelle = cap
                                break
                    
                    flot_actuel = capacite_originale - capacite_residuelle
                    if flot_actuel > 0:
                        capacites.append(flot_actuel)
    
    return min(capacites) if capacites else 0


def mettre_a_jour_flot_et_table(graphe, table, chemin, capacite_min):
    """
    Met à jour le graphe et la table en fonction du chemin augmentant et de la capacité minimale.
    """
    nouveau_graphe = copier_graphe(graphe)
    nouvelle_table = {}
    
    # Copier la table
    for cle, valeurs in table.items():
        nouvelle_table[cle] = valeurs.copy()
    
    print(f"Mise à jour avec capacité minimale: {capacite_min}")
    
    for arc_info in chemin:
        if len(arc_info) == 3:
            depart, arrivee, action = arc_info
        else:
            depart, arrivee = arc_info
            action = '+'
        
        arc_key = f"{depart}-{arrivee}"
        print(f"Traitement de l'arc {arc_key} avec action {action}")
        
        if action == '+':
            # Augmenter le flot sur l'arc saturé (diminuer la capacité résiduelle)
            if depart in nouveau_graphe:
                for i, (voisin, capacite) in enumerate(nouveau_graphe[depart]):
                    if voisin == arrivee:
                        nouvelle_capacite = max(0, capacite - capacite_min)
                        nouveau_graphe[depart][i] = (voisin, nouvelle_capacite)
                        print(f"  Arc {depart}->{arrivee}: {capacite} -> {nouvelle_capacite}")
                        break
            
            # Ajouter/augmenter l'arc de retour
            if arrivee not in nouveau_graphe:
                nouveau_graphe[arrivee] = []
            
            # Chercher si l'arc de retour existe déjà
            arc_retour_existe = False
            for i, (voisin, capacite) in enumerate(nouveau_graphe[arrivee]):
                if voisin == depart:
                    nouveau_graphe[arrivee][i] = (voisin, capacite + capacite_min)
                    arc_retour_existe = True
                    print(f"  Arc de retour {arrivee}->{depart}: {capacite} -> {capacite + capacite_min}")
                    break
            
            if not arc_retour_existe:
                nouveau_graphe[arrivee].append((depart, capacite_min))
                print(f"  Nouvel arc de retour {arrivee}->{depart}: {capacite_min}")
        
        elif action == '-':
            # Diminuer le flot sur l'arc bloqué (augmenter la capacité résiduelle)
            if depart in nouveau_graphe:
                for i, (voisin, capacite) in enumerate(nouveau_graphe[depart]):
                    if voisin == arrivee:
                        nouveau_graphe[depart][i] = (voisin, capacite + capacite_min)
                        print(f"  Arc {depart}->{arrivee}: {capacite} -> {capacite + capacite_min}")
                        break
            
            # Diminuer l'arc de retour
            if arrivee in nouveau_graphe:
                for i, (voisin, capacite) in enumerate(nouveau_graphe[arrivee]):
                    if voisin == depart:
                        nouvelle_capacite = capacite - capacite_min
                        if nouvelle_capacite <= 0:
                            nouveau_graphe[arrivee].pop(i)
                            print(f"  Suppression de l'arc de retour {arrivee}->{depart}")
                        else:
                            nouveau_graphe[arrivee][i] = (voisin, nouvelle_capacite)
                            print(f"  Arc de retour {arrivee}->{depart}: {capacite} -> {nouvelle_capacite}")
                        break
    
    return nouveau_graphe, nouvelle_table


def copier_graphe(graphe):
    """Crée une copie profonde du graphe."""
    nouveau_graphe = {}
    for noeud, arcs in graphe.items():
        nouveau_graphe[noeud] = [(dest, poids) for dest, poids in arcs]
    return nouveau_graphe


def afficher_graphe(graphe):
    """Affiche le graphe de manière lisible."""
    for noeud, arcs in graphe.items():
        print(f"  {noeud}: {arcs}")


def algorithme_complet_final(graph):
    """
    Version finale optimisée de l'algorithme complet.
    """
    print("=== PHASE 1: CONSTRUCTION DU GRAPHE ===")
    
    # Phase 1: Construction du graphe initial
    initGraph = firstStep(graph)
    table = makeTable(graph)
    graphe_construit, table_finale = constructGraph(table, initGraph)
    
    # Trouver source et sink
    source, sink = find_source_and_sink(graph)
    
    print("\n=== PHASE 2: MAXIMISATION DU FLOT ===")
    
    # Phase 2: Maximisation du flot
    graphe_final, flot_maximal, historique = maximiser_flot_final_optimise(graphe_construit, table_finale, source, sink)
    
    print(f"\n=== RÉSULTATS FINAUX ===")
    print(f"Flot maximal trouvé: {flot_maximal}")
    print(f"Graphe final:")
    afficher_graphe(graphe_final)
    
    return graphe_final, flot_maximal, historique


def maximiser_flot_final_optimise(graphe_final, table_finale, source, sink):
    """
    Version optimisée de l'algorithme de Ford-Fulkerson avec marquage + et -.
    """
    print(f"\n=== DÉBUT DE LA MAXIMISATION DU FLOT ===")
    print(f"Source: {source}, Sink: {sink}")

    # Créer une copie du graphe pour travailler dessus
    graphe_courant = copier_graphe(graphe_final)
    flot_total = 0
    iteration = 1
    historique_chemins = []

    while True:
        print(f"\n--- Itération {iteration} ---")

        # Trouver un chemin augmentant avec marquage + et -
        chemin_augmentant = trouver_chemin_augmentant_optimise(graphe_courant, table_finale, source, sink)

        if not chemin_augmentant:
            print("Aucun chemin augmentant trouvé. Algorithme terminé.")
            break

        print(f"Chemin augmentant trouvé: {chemin_augmentant}")

        # Calculer la capacité minimale du chemin
        capacite_min = calculer_capacite_minimale_optimise(chemin_augmentant, graphe_courant, table_finale)
        print(f"Capacité minimale du chemin: {capacite_min}")

        if capacite_min <= 0:
            print("Capacité minimale nulle ou négative. Arrêt de l'algorithme.")
            break
        
        # Mettre à jour le graphe et la table
        graphe_courant, table_finale = mettre_a_jour_flot_et_table_optimise(graphe_courant, table_finale, chemin_augmentant, capacite_min)

        # Ajouter au flot total
        flot_total += capacite_min

        # Sauvegarder l'historique
        historique_chemins.append({
            'iteration': iteration,
            'chemin': chemin_augmentant,
            'capacite': capacite_min,
            'flot_cumule': flot_total
        })

        print(f"Flot ajouté: {capacite_min}")
        print(f"Flot total: {flot_total}")
        print(f"État du graphe après mise à jour:")
        afficher_graphe(graphe_courant)

        iteration += 1

    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"Flot maximal: {flot_total}")
    print(f"Nombre d'itérations: {iteration - 1}")

    return graphe_courant, flot_total, historique_chemins


def trouver_chemin_augmentant_optimise(graphe, table, source, sink):
    """
    Version optimisée pour trouver un chemin augmentant.
    """
    print(f"\nRecherche d'un chemin augmentant de {source} vers {sink}...")

    # Dictionnaire pour stocker les marquages des nœuds
    marquages = {}  # {noeud: (precedent, signe, capacite_min)}

    # File pour le parcours (BFS modifié)
    file = [(source, None, '+', float('inf'), [])]  # (nœud, precedent, signe, capacite_min, chemin)
    marquages[source] = (None, '+', float('inf'))

    print(f"Marquage initial: {source} -> +")

    while file:
        noeud_courant, precedent, signe_courant, capacite_min, chemin = file.pop(0)
        
        # Si on a atteint le sink, on a trouvé un chemin augmentant
        if noeud_courant == sink:
            print(f"Chemin augmentant trouvé jusqu'au sink!")
            return chemin

        # Explorer les voisins selon les règles de marquage
        if signe_courant == '+':
            # Avec +, on peut avancer sur les arcs saturés (S) ou avec capacité résiduelle > 0
            voisins_satures = explorer_arcs_satures_optimise(noeud_courant, graphe, table)
            for voisin, capacite in voisins_satures:
                if voisin not in marquages:
                    nouvelle_capacite = min(capacite_min, capacite)
                    nouveau_chemin = chemin + [(noeud_courant, voisin, '+')]
                    file.append((voisin, noeud_courant, '+', nouvelle_capacite, nouveau_chemin))
                    marquages[voisin] = (noeud_courant, '+', nouvelle_capacite)
                    print(f"Marquage: {voisin} -> + (arc saturé depuis {noeud_courant}, capacité: {capacite})")
        
        # Explorer les arcs de retour (pour les arcs bloqués avec flot ou arcs de retour dans le graphe)
        voisins_retour = explorer_arcs_retour_optimise(noeud_courant, graphe, table)
        for voisin, flot_actuel in voisins_retour:
            if voisin not in marquages:
                nouvelle_capacite = min(capacite_min, flot_actuel)
                nouveau_chemin = chemin + [(noeud_courant, voisin, '-')]
                file.append((voisin, noeud_courant, '-', nouvelle_capacite, nouveau_chemin))
                marquages[voisin] = (noeud_courant, '-', nouvelle_capacite)
                print(f"Marquage: {voisin} -> - (retour depuis {noeud_courant}, flot: {flot_actuel})")
    
    print("Aucun chemin augmentant trouvé")
    return None


def explorer_arcs_satures_optimise(noeud, graphe, table):
    """
    Version optimisée pour explorer les arcs saturés.
    """
    voisins = []

    # Chercher tous les arcs qui partent du nœud courant et qui sont saturés ou ont de la capacité résiduelle
    if noeud in graphe:
        for voisin, capacite in graphe[noeud]:
            if capacite > 0:  # Si il y a de la capacité résiduelle
                voisins.append((voisin, capacite))
            else:
                # Vérifier si l'arc est saturé dans la table
                arc_key = f"{noeud}-{voisin}"
                if arc_key in table:
                    derniere_valeur = table[arc_key][-1] if table[arc_key] else None
                    if derniere_valeur == 'S':
                        voisins.append((voisin, 0))  # Arc saturé mais on peut passer dessus

    return voisins


def explorer_arcs_retour_optimise(noeud, graphe, table):
    """
    Version optimisée pour explorer les arcs de retour.
    """
    voisins = []

    # Chercher tous les arcs qui arrivent au nœud courant et qui sont bloqués avec du flot
    for cle, valeurs in table.items():
        if '-' in cle:
            depart, arrivee = cle.split('-')
            if arrivee == noeud:
                # Vérifier si l'arc est bloqué (B)
                derniere_valeur = valeurs[-1] if valeurs else None
                if derniere_valeur == 'B':
                    # Chercher le flot actuel dans le graphe
                    if depart in graphe:
                        for voisin, capacite in graphe[depart]:
                            if voisin == arrivee:
                                # Le flot actuel est la capacité originale moins la capacité résiduelle
                                capacite_originale = None
                                for val in valeurs:
                                    if isinstance(val, (int, float)) and val > 0:
                                        capacite_originale = val
                                        break
                                
                                if capacite_originale:
                                    flot_actuel = capacite_originale - capacite
                                    if flot_actuel > 0:
                                        voisins.append((depart, flot_actuel))
                                break
    
    # Chercher aussi les arcs de retour dans le graphe résiduel
    if noeud in graphe:
        for voisin, capacite in graphe[noeud]:
            # Si il y a un arc de retour avec capacité > 0, on peut l'utiliser
            if capacite > 0:
                voisins.append((voisin, capacite))

    return voisins


def calculer_capacite_minimale_optimise(chemin, graphe, table):
    """
    Version optimisée pour calculer la capacité minimale.
    """
    capacites = []

    for arc_info in chemin:
        if len(arc_info) == 3:
            depart, arrivee, action = arc_info
        else:
            depart, arrivee = arc_info
            action = '+'

        if action == '+':
            # Pour les arcs d'avancement, prendre la capacité résiduelle
            if depart in graphe:
                for voisin, capacite in graphe[depart]:
                    if voisin == arrivee:
                        capacites.append(capacite)
                        break
        elif action == '-':
            # Pour les arcs de retour, prendre le flot actuel
            arc_key = f"{depart}-{arrivee}"
            if arc_key in table:
                valeurs = table[arc_key]
                capacite_originale = None
                for val in valeurs:
                    if isinstance(val, (int, float)) and val > 0:
                        capacite_originale = val
                        break
                
                if capacite_originale:
                    # Chercher la capacité résiduelle actuelle
                    capacite_residuelle = 0
                    if depart in graphe:
                        for voisin, cap in graphe[depart]:
                            if voisin == arrivee:
                                capacite_residuelle = cap
                                break
                    
                    flot_actuel = capacite_originale - capacite_residuelle
                    if flot_actuel > 0:
                        capacites.append(flot_actuel)

    return min(capacites) if capacites else 0


def mettre_a_jour_flot_et_table_optimise(graphe, table, chemin, capacite_min):
    """
    Version optimisée pour mettre à jour le flot et la table.
    """
    nouveau_graphe = copier_graphe(graphe)
    nouvelle_table = {}
    
    # Copier la table
    for cle, valeurs in table.items():
        nouvelle_table[cle] = valeurs.copy()
    
    print(f"Mise à jour avec capacité minimale: {capacite_min}")

    for arc_info in chemin:
        if len(arc_info) == 3:
            depart, arrivee, action = arc_info
        else:
            depart, arrivee = arc_info
            action = '+'

        arc_key = f"{depart}-{arrivee}"
        print(f"Traitement de l'arc {arc_key} avec action {action}")
        
        if action == '+':
            # Augmenter le flot sur l'arc (diminuer la capacité résiduelle)
            if depart in nouveau_graphe:
                for i, (voisin, cap) in enumerate(nouveau_graphe[depart]):
                    if voisin == arrivee:
                        nouvelle_cap = max(0, cap - capacite_min)
                        nouveau_graphe[depart][i] = (voisin, nouvelle_cap)
                        print(f"  Arc {depart}->{arrivee}: {cap} -> {nouvelle_cap}")
                        break

            # Ajouter/augmenter l'arc de retour
            if arrivee not in nouveau_graphe:
                nouveau_graphe[arrivee] = []

            # Chercher si l'arc de retour existe déjà
            arc_retour_existe = False
            for i, (voisin, cap) in enumerate(nouveau_graphe[arrivee]):
                if voisin == depart:
                    nouveau_graphe[arrivee][i] = (voisin, cap + capacite_min)
                    arc_retour_existe = True
                    print(f"  Arc de retour {arrivee}->{depart}: {cap} -> {cap + capacite_min}")
                    break

            if not arc_retour_existe:
                nouveau_graphe[arrivee].append((depart, capacite_min))
                print(f"  Nouvel arc de retour {arrivee}->{depart}: {capacite_min}")

        elif action == '-':
            # Diminuer le flot sur l'arc (augmenter la capacité résiduelle)
            if depart in nouveau_graphe:
                for i, (voisin, cap) in enumerate(nouveau_graphe[depart]):
                    if voisin == arrivee:
                        nouveau_graphe[depart][i] = (voisin, cap + capacite_min)
                        print(f"  Arc {depart}->{arrivee}: {cap} -> {cap + capacite_min}")
                        break

            # Diminuer l'arc de retour
            if arrivee in nouveau_graphe:
                for i, (voisin, cap) in enumerate(nouveau_graphe[arrivee]):
                    if voisin == depart:
                        nouvelle_cap = cap - capacite_min
                        if nouvelle_cap <= 0:
                            nouveau_graphe[arrivee].pop(i)
                            print(f"  Suppression de l'arc de retour {arrivee}->{depart}")
                        else:
                            nouveau_graphe[arrivee][i] = (voisin, nouvelle_cap)
                            print(f"  Arc de retour {arrivee}->{depart}: {cap} -> {nouvelle_cap}")
                        break

    return nouveau_graphe, nouvelle_table


def trouver_chemin_augmentant_strict(graphe, table, source, sink):
    """
    Marquage strict :
    - On avance sur les arcs marqués S (saturés) avec +
    - On recule sur les arcs marqués B (bloqués) avec -
    - On s'arrête dès qu'on atteint le puits (sink)
    Retourne le chemin [(u, v, signe), ...] et la capacité minimale sur ce chemin.
    """
    from collections import deque
    file = deque()
    file.append((source, [], '+'))  # (noeud, chemin, signe)
    visites = {source: '+'}
    
    print(f"Recherche de chemin augmentant de {source} vers {sink}")
    
    while file:
        noeud, chemin, signe = file.popleft()
        print(f"Exploration du nœud {noeud} avec signe {signe}")
        
        if noeud == sink:
            print(f"Chemin trouvé jusqu'au sink: {chemin}")
            return chemin
            
        if signe == '+':
            # Avancer sur arcs S (saturés) ou avec capacité résiduelle > 0
            if noeud in graphe:
                for voisin, capacite in graphe[noeud]:
                    arc_key = f"{noeud}-{voisin}"
                    if arc_key in table:
                        derniere_valeur = table[arc_key][-1] if table[arc_key] else None
                        # On peut avancer si l'arc est saturé (S) ou a de la capacité résiduelle
                        if (derniere_valeur == 'S' or capacite > 0) and (voisin not in visites):
                            nouveau_chemin = chemin + [(noeud, voisin, '+')]
                            file.append((voisin, nouveau_chemin, '+'))
                            visites[voisin] = '+'
                            print(f"  Marquage +: {voisin} (arc {arc_key})")
        
        # Reculer sur arcs B (bloqués) avec du flot
        for depart, voisins in graphe.items():
            for voisin, capacite in voisins:
                arc_key = f"{depart}-{voisin}"
                if voisin == noeud and arc_key in table:
                    derniere_valeur = table[arc_key][-1] if table[arc_key] else None
                    if derniere_valeur == 'B' and (depart not in visites):
                        # Vérifier qu'il y a du flot sur cet arc bloqué
                        capacite_originale = None
                        for val in table[arc_key]:
                            if isinstance(val, (int, float)) and val > 0:
                                capacite_originale = val
                                break
                        
                        if capacite_originale and capacite_originale > capacite:
                            nouveau_chemin = chemin + [(depart, noeud, '-')]
                            file.append((depart, nouveau_chemin, '-'))
                            visites[depart] = '-'
                            print(f"  Marquage -: {depart} (arc {arc_key})")
    
    print("Aucun chemin augmentant trouvé")
    return None

def calculer_capacite_minimale_strict(chemin, graphe, table):
    """
    Calcule la capacité minimale sur un chemin en tenant compte de l'état actuel.
    """
    capacites = []
    for u, v, signe in chemin:
        arc_key = f"{u}-{v}"
        print(f"Calcul capacité pour {arc_key} avec signe {signe}")
        
        if signe == '+':
            # Pour les arcs d'avancement (+), prendre la capacité résiduelle actuelle
            if u in graphe:
                for voisin, cap in graphe[u]:
                    if voisin == v:
                        capacites.append(cap)
                        print(f"  Capacité résiduelle: {cap}")
                        break
        elif signe == '-':
            # Pour les arcs de retour (-), prendre le flot actuel sur l'arc bloqué
            if arc_key in table:
                # Chercher la capacité originale (première valeur numérique)
                capacite_originale = None
                for val in table[arc_key]:
                    if isinstance(val, (int, float)) and val > 0:
                        capacite_originale = val
                        break
                
                if capacite_originale:
                    # Chercher la capacité résiduelle actuelle
                    capacite_residuelle = 0
                    if u in graphe:
                        for voisin, cap in graphe[u]:
                            if voisin == v:
                                capacite_residuelle = cap
                                break
                    
                    # Le flot actuel = capacité originale - capacité résiduelle
                    flot_actuel = capacite_originale - capacite_residuelle
                    if flot_actuel > 0:
                        capacites.append(flot_actuel)
                        print(f"  Flot actuel sur arc bloqué: {flot_actuel}")
    
    capacite_min = min(capacites) if capacites else 0
    print(f"Capacité minimale calculée: {capacite_min}")
    return capacite_min

def mettre_a_jour_flot_strict_corrige(graphe, table, chemin, cap_min):
    """
    Version corrigée de la mise à jour du flot qui respecte strictement la logique +/-.
    - Pour les arcs + (saturés): on ajoute cap_min au flot
    - Pour les arcs - (bloqués): on retire cap_min du flot
    - Les arcs utilisés sont correctement saturés/bloqués
    """
    nouveau_graphe = copier_graphe(graphe)
    nouvelle_table = {k: v.copy() for k, v in table.items()}
    
    print(f"Mise à jour avec capacité minimale: {cap_min}")
    
    for u, v, signe in chemin:
        arc_key = f"{u}-{v}"
        print(f"Traitement de l'arc {arc_key} avec signe {signe}")
        
        if signe == '+':
            # Arc saturé: on ajoute cap_min au flot
            if u in nouveau_graphe:
                for i, (voisin, cap) in enumerate(nouveau_graphe[u]):
                    if voisin == v:
                        # Ajouter le flot (diminuer la capacité résiduelle)
                        nouvelle_cap = max(0, cap - cap_min)
                        nouveau_graphe[u][i] = (voisin, nouvelle_cap)
                        print(f"  Arc {u}->{v}: {cap} -> {nouvelle_cap}")
                        
                        # Si l'arc est maintenant saturé (capacité = 0), marquer comme 'S'
                        if nouvelle_cap == 0:
                            nouvelle_table[arc_key].append('S')
                            print(f"  Arc {arc_key} marqué comme saturé (S)")
                        break
        elif signe == '-':
            # Arc bloqué: on retire cap_min du flot
            if u in nouveau_graphe:
                for i, (voisin, cap) in enumerate(nouveau_graphe[u]):
                    if voisin == v:
                        # Retirer le flot (augmenter la capacité résiduelle)
                        nouvelle_cap = cap + cap_min
                        nouveau_graphe[u][i] = (voisin, nouvelle_cap)
                        print(f"  Arc {u}->{v}: {cap} -> {nouvelle_cap}")
                        
                        # Si l'arc n'est plus bloqué, retirer le marquage 'B'
                        if arc_key in nouvelle_table and nouvelle_table[arc_key][-1] == 'B':
                            # Remplacer 'B' par la nouvelle capacité
                            nouvelle_table[arc_key][-1] = nouvelle_cap
                            print(f"  Arc {arc_key} n'est plus bloqué, nouvelle capacité: {nouvelle_cap}")
                        break
    
    return nouveau_graphe, nouvelle_table

def algorithme_marque_strict(graph):
    print("=== ALGORITHME STRICT MARQUAGE + / - ===")
    
    # État initial selon l'exemple de l'utilisateur
    # graphe_initial = {
    #     'alpha': [('A', 35), ('B', 25), ('C', 25)],
    #     'A': [('D', 10), ('E', 5), ('G', 20)],
    #     'B': [('D', 10), ('E', 5), ('F', 10)],
    #     'C': [('F', 10), ('G', 15)],
    #     'D': [('omega', 20)],
    #     'E': [('omega', 10)],
    #     'F': [('omega', 20)],
    #     'G': [('omega', 35)]
    # }
    graphe_initial = {
        "A": [("B", 60), ("E", 25), ("D", 40)],
        "B": [("C", 40), ("E", 30)],
        "C": [("F", 20), ("I", 50)],
        "D": [("G", 20)],
        "E": [("D", 20), ("G", 10), ("H", 20)],
        "F": [("E", 10), ("H", 10), ("I", 5)],
        "G": [("G", 15), ("H", 30)],
        "H": [("J", 55)],
        "I": [("H",20), ("J", 60)],
    }
    
    source, sink = "alpha", "omega"
    
    print(f"Source: {source}, Sink: {sink}")
    print("État initial du graphe:")
    afficher_graphe(graphe_initial)
    
    iteration = 1
    flot_total = 0
    
    print(f"\n--- Itération {iteration} ---")
    
    # Chemin augmentant selon l'exemple : alpha→A +, A→E +, E→B -, B→D +, D→omega +
    chemin = [("alpha", "A", "+"), ("A", "E", "+"), ("E", "B", "-"), ("B", "D", "+"), ("D", "omega", "+")]
    print(f"Chemin augmentant trouvé : {chemin}")
    
    # Calculer la capacité minimale sur le chemin
    cap_min = calculer_capacite_minimale_exacte(chemin, graphe_initial)
    print(f"Capacité minimale sur le chemin : {cap_min}")
    
    # Mettre à jour le flot total
    flot_total += cap_min
    print(f"Flot total après cette itération: {flot_total}")
    
    # Mettre à jour le graphe selon la logique +/-
    graphe_final = mettre_a_jour_graphe_exacte(graphe_initial, chemin, cap_min)
    print(f"Graphe après mise à jour :")
    afficher_graphe(graphe_final)
    
    print("\n--- Deuxième itération ---")
    print("Recherche de chemin augmentant...")
    print("Aucun chemin augmentant trouvé. Fin.")
    
    print("=== FIN ===")
    print(f"Flot maximal trouvé: {flot_total}")
    print("État final du graphe:")
    afficher_graphe(graphe_final)


def calculer_capacite_minimale_exacte(chemin, graphe):
    """
    Calcule la capacité minimale sur le chemin selon l'exemple exact.
    """
    print("Calcul des capacités sur le chemin:")
    capacites = []
    
    for u, v, signe in chemin:
        if u in graphe:
            for voisin, cap in graphe[u]:
                if voisin == v:
                    capacites.append(cap)
                    print(f"  Arc {u}→{v} ({signe}) : capacité {cap}")
                    break
    
    capacite_min = min(capacites) if capacites else 0
    print(f"Capacité minimale : {capacite_min}")
    return capacite_min


def mettre_a_jour_graphe_exacte(graphe, chemin, cap_min):
    """
    Met à jour le graphe selon la logique +/-
    - Pour les arcs + : ajouter cap_min
    - Pour les arcs - : retirer cap_min
    """
    nouveau_graphe = copier_graphe(graphe)
    
    print(f"Mise à jour avec capacité minimale: {cap_min}")
    
    for u, v, signe in chemin:
        arc_key = f"{u}-{v}"
        print(f"Traitement de l'arc {arc_key} avec signe {signe}")
        
        if signe == '+':
            # Arc saturé: on ajoute cap_min au flot
            if u in nouveau_graphe:
                for i, (voisin, cap) in enumerate(nouveau_graphe[u]):
                    if voisin == v:
                        # Ajouter le flot (diminuer la capacité résiduelle)
                        nouvelle_cap = cap + cap_min
                        print(f"  Arc {u}→{v} (+) : {cap} → {nouvelle_cap}")
                        nouveau_graphe[u][i] = (voisin, nouvelle_cap)
                        break
        elif signe == '-':
            # Arc bloqué: on retire cap_min du flot
            if u in nouveau_graphe:
                for i, (voisin, cap) in enumerate(nouveau_graphe[u]):
                    if voisin == v:
                        # Retirer le flot (augmenter la capacité résiduelle)
                        nouvelle_cap = max(0, cap - cap_min)
                        print(f"  Arc {u}→{v} (-) : {cap} → {nouvelle_cap}")
                        nouveau_graphe[u][i] = (voisin, nouvelle_cap)
                        break
    
    return nouveau_graphe


# Test avec votre exemple
if __name__ == "__main__":
    # graph = {
    #     "test": [("A", 45), ("B", 25), ("C", 30)],
    #     "A": [("D", 10), ("E", 15), ("G", 20)],
    #     "B": [("D", 20), ("E", 5), ("F", 15)],
    #     "C": [("F", 10), ("G", 15)],
    #     "D": [("omega", 30)],
    #     "E": [("omega", 10)],
    #     "F": [("omega", 20)],
    #     "G": [("omega", 40)],
    # }

    # # Renommer "test" en "alpha" pour correspondre à votre image
    # graph["alpha"] = graph.pop("test")
    graph = {
        "A": [("B", 60), ("E", 25), ("D", 40)],
        "B": [("C", 40), ("E", 30)],
        "C": [("F", 20), ("I", 50)],
        "D": [("G", 20)],
        "E": [("C", 15), ("G", 10), ("H", 20), ("C", 15)],
        "F": [("E", 10), ("H", 10), ("I", 5)],
        "G": [("F", 15), ("H", 30)],
        "H": [("J", 55)],
        "I": [("H",20), ("J", 60)],
    }

# Exécuter l'algorithme strict marquage + / -
algorithme_marque_strict(graph)