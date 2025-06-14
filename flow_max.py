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


if __name__ == "__main__":
    # Test avec votre graphe modifié
    graph = {
        "test": [("A", 45), ("B", 25), ("C", 30)],
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
    constructGraph(table, intiGraph)


    # def update_flow_graph(marked_path, flow, cap_back):
    #     capacite_dict = {(u, v): cap for (u, v, cap) in flow}
    #
    #     for (arc, signe, val) in marked_path:
    #         u, v = arc
    #         if signe == '+':
    #             capacite_dict[(u, v)] = capacite_dict.get((u, v), 0) + cap_back
    #         elif signe == '-':
    #             print("Capacité avant modification:", capacite_dict[(u, v)])
    #             capacite_dict[(u, v)] = capacite_dict.get((u, v), 0) - cap_back
    #             print("Capacité après modification:", capacite_dict[(u, v)])
    #
    #     new_flow = [(u, v, cap) for ((u, v), cap) in capacite_dict.items()]
    #     return new_flow