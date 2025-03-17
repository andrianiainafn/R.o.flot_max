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


def constructGraph(t, graph):
    """
    Construit le graphe en mettant à jour ses arcs et la table de façon itérative.

    Args:
        t (dict): La table des arcs
        graph (dict): Le graphe initial

    Returns:
        tuple: (graphe mis à jour, table mise à jour)
    """
    graphe_maj = graph.copy()  # Copier le graphe pour éviter de modifier l'original
    premiere_cle, premiere_valeur = next(iter(t.items()))

    for n in range(3):  # Boucler deux fois comme dans votre code original
        # Initialiser minim à la première valeur de la colonne n
        minim = premiere_valeur[n]
        if minim in ["S", "B"]:
            minim = float('inf')  # Valeur infinie si la première valeur est "S" ou "B"
        else:
            minim = float(minim)  # Convertir en nombre si ce n'est pas déjà le cas

        arc, minim = getMinimArc(t, n, minim)
        print(f"Itération {n + 1}, Arc sélectionné: {arc}, Valeur minimale: {minim}")

        # Utiliser la table pour la vérification des chemins bloqués/saturés
        graphe_maj, arcs_modifies = mettre_a_jour_arc(graphe_maj, arc[0], arc[1], minim, t)
        print(f"Arcs modifiés: {arcs_modifies}")

        # Mettre à jour la table avec les nouvelles valeurs
        t = mettre_a_jour_table(t, n + 1, minim, graphe_maj, arcs_modifies, arc)

        # Afficher l'état actuel du graphe et de la table
        print(f"Table après itération {n + 1}:", {k: v[:n + 2] for k, v in t.items()})
        print(f"Graphe après itération {n + 1}:", graphe_maj)

    return graphe_maj, t


def getMinimArc(t, n, startMinim):
    """
    Trouve l'arc avec la valeur minimale dans la colonne n de la table.

    Args:
        t (dict): La table des arcs
        n (int): L'indice de la colonne à vérifier
        startMinim (float): La valeur minimale de départ

    Returns:
        tuple: (arc, valeur minimale)
    """
    minim = startMinim if startMinim != 0 else float('inf')
    minim_key = ""

    for key, value in t.items():
        # Ignorer les arcs marqués comme "S" ou "B"
        if n < len(value) and value[n] not in ["S", "B"] and isinstance(value[n], (int, float)):
            current_val = float(value[n])
            if current_val < minim:
                minim = current_val
                minim_key = key

    if minim_key:
        arc = minim_key.split("-")
        return arc, minim
    else:
        return None, float('inf')  # Retourner None si aucun arc valide n'est trouvé


def mettre_a_jour_table(t, index, minim, graph, arcs_modifies, arcs):
    a_verifier = "-".join(arcs)
    print("arc", a_verifier)
    blocked = check_if_blocked(a_verifier, t, graph)
    print("bloquer", blocked)

    if blocked:
        # Si l'arc est bloqué, marquer toutes les colonnes restantes comme 'B'
        for i in range(index, len(t[a_verifier])):
            t[a_verifier][i] = 'B'
        print("blocked-arcs", t[a_verifier])
    else:
        for key, value in t.items():
            # Ignorer les entrées déjà marquées comme 'S' ou 'B'
            if index > 0 and (value[index - 1] == "S" or value[index - 1] == "B"):
                value[index] = value[index - 1]  # Conserver la même marque
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


def check_if_blocked(arc_requis, table, graph):
    # Trouver tous les chemins qui contiennent l'arc requis
    chemins = trouver_chemins_avec_arc(graph, arc_requis)

    if not chemins:
        # Si aucun chemin ne contient cet arc, on considère qu'il est bloqué
        return True

    # Vérifier chaque chemin
    tous_bloques = True
    for chemin in chemins:
        chemin_bloque = False

        # Vérifier chaque arc du chemin sauf celui qui est requis
        for depart, arrivee in chemin:
            if f"{depart}-{arrivee}" == arc_requis:
                continue

            # Vérifier si l'arc est dans la table et s'il est marqué comme "S" ou "B"
            arc_key = f"{depart}-{arrivee}"
            if arc_key in table:
                # Vérifier la dernière valeur non nulle
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

        # Si au moins un chemin n'est pas bloqué, alors l'arc n'est pas totalement bloqué
        if not chemin_bloque:
            tous_bloques = False
            break

    return tous_bloques


def mettre_a_jour_arc(graphe, depart, arrivee, valeur, table=None):
    """
    Met à jour les arcs du graphe qui font partie des chemins contenant l'arc spécifié.
    Ne met à jour que les chemins qui ne sont pas bloqués ou saturés.

    Args:
        graphe (dict): Le graphe à mettre à jour
        depart (str): Le nœud de départ de l'arc
        arrivee (str): Le nœud d'arrivée de l'arc
        valeur (int): La valeur à ajouter aux arcs
        table (dict, optional): La table des arcs pour vérifier les arcs bloqués ou saturés

    Returns:
        tuple: (graphe mis à jour, liste des arcs modifiés)
    """
    # Récupérer les chemins qui contiennent l'arc
    chemins_potentiels = trouver_chemins_avec_arc(graphe, f"{depart}-{arrivee}")
    print(f"Chemins potentiels pour {depart}-{arrivee}:", chemins_potentiels)

    # Filtrer les chemins qui ne sont pas bloqués ou saturés
    chemins_valides = []
    if table:
        for chemin in chemins_potentiels:
            chemin_valide = True
            for source, destination in chemin:
                arc_key = f"{source}-{destination}"
                if arc_key in table:
                    for val in table[arc_key]:
                        if val in ["S", "B"]:
                            chemin_valide = False
                            print(f"Chemin bloqué ou saturé à l'arc {arc_key}: {table[arc_key]}")
                            break
                if not chemin_valide:
                    break

            if chemin_valide:
                chemins_valides.append(chemin)
    else:
        chemins_valides = chemins_potentiels

    print(f"Chemins valides pour {depart}-{arrivee}:", chemins_valides)

    # Mettre à jour seulement les arcs des chemins valides
    for chemin in chemins_valides:
        for source, destination in chemin:
            if source in graphe:
                for j, (dest, poids) in enumerate(graphe[source]):
                    if dest == destination:
                        graphe[source][j] = (dest, poids + valeur)
                        print(f"Mise à jour de l'arc {source}-{destination}: {poids} -> {poids + valeur}")
                        break

    # Convertir chemins_valides en liste simple d'arcs pour la mise à jour de la table
    arcs_modifies = [f"{source}-{destination}" for chemin in chemins_valides for source, destination in chemin]
    arcs_modifies = list(set(arcs_modifies))  # Éliminer les doublons

    return graphe, arcs_modifies


def trouver_chemins_avec_arc(graph, arc_requis):
    # Vérifier si arc_requis est une chaîne et la convertir en tuple si nécessaire
    if isinstance(arc_requis, str):
        debut, fin = arc_requis.split("-")
    else:
        debut, fin = arc_requis

    # Trouver tous les chemins de 'alfa' à début
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

    # Commencer la recherche depuis 'alfa'
    dfs_vers_debut("alfa", [])

    # Trouver tous les chemins de fin à 'omega'
    chemins_vers_omega = []

    def dfs_vers_omega(noeud_courant, chemin_courant):
        if noeud_courant == "omega":
            chemins_vers_omega.append(list(chemin_courant))
            return

        for voisin, poids in graph.get(noeud_courant, []):
            if not any(arc[0] == voisin for arc in chemin_courant):
                chemin_courant.append((noeud_courant, voisin))
                dfs_vers_omega(voisin, chemin_courant)
                chemin_courant.pop()

    # Commencer la recherche depuis le nœud de fin de l'arc requis
    dfs_vers_omega(fin, [])

    # Combiner les chemins pour obtenir les chemins complets
    chemins_complets = []

    for chemin_debut in chemins_vers_debut:
        for chemin_fin in chemins_vers_omega:
            chemin_complet = list(chemin_debut)
            chemin_complet.append((debut, fin))  # Ajouter l'arc requis
            chemin_complet.extend(chemin_fin)
            chemins_complets.append(chemin_complet)

    return chemins_complets


if __name__ == "__main__":
    graph = {
        "alfa": [("A", 45), ("B", 25), ("C", 30)],
        "A": [("D", 10), ("E", 15), ("G", 20)],
        "B": [("D", 20), ("E", 5), ("F", 15)],
        "C": [("F", 10), ("G", 15)],
        "D": [("omega", 30)],
        "E": [("omega", 10)],
        "F": [("omega", 20)],
        "G": [("omega", 40)],
    }

    intiGraph = firstStep(graph)
    table = makeTable(graph)
    # print(table)
    constructGraph(table, intiGraph)
    # print(intiGraph)
    # for key, value in table.items():
    #     print(f"{key}: {value}")