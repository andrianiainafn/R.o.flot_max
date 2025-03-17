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
    graphe_maj=graph
    premiere_cle, premiere_valeur = next(iter(t.items()))
    for n in range(0,2):
        minim = premiere_valeur[n]
        arc, minim = getMinimArc(t, n, minim)
        # print("minim",arc)
        # print(arc, minim)
        # print(intiGraph)
        graphe_maj, arcs_modifies = mettre_a_jour_arc(graphe_maj, arc[0], arc[1], minim)
        t = mettre_a_jour_table(t, n+1, minim, graphe_maj, arcs_modifies,arc)
    print("table",t)
    print("graphe_maj",graphe_maj)

def getMinimArc(t,n,startMinim):
    minim = startMinim
    print(startMinim)
    minim_key = ""
    for key,value in t.items():
        if value[n] == "S" or value[n] == "B":
            continue
        elif minim > value[n] :
            minim = value[n]
            minim_key = key
    arc = minim_key.split("-")
    return arc,minim
def mettre_a_jour_table(t,index,minim,graph,arc_modifies,arcs):
    a_verifier = "-".join(arcs)
    chemin = trouver_chemins_avec_arc(graph,a_verifier)
    print("chemin",chemin)
    for key,value in t.items():
        if value[index] == "S" or value[index] == "B":
            continue
        if key in arc_modifies :
            value[index] = value[index - 1] - minim
            if value[index] == 0:
                value[index - 1:] = ['S'] * (len(value) - (index + 1))
        else:
            value[index] = value[index - 1]
    # print(t)
    return t
def check_if_blocked():
    print("Blocked")

def mettre_a_jour_arc(graphe, depart, arrivee, valeur):
    arcs_modifies = []

    # Vérifier si l'arc existe directement
    if depart in graphe and any(dest == arrivee for dest, _ in graphe[depart]):
        # Mettre à jour l'arc direct
        for i, (dest, _) in enumerate(graphe[depart]):
            if dest == arrivee:
                ancienne_valeur = graphe[depart][i][1]
                graphe[depart][i] = (arrivee, valeur)
                arcs_modifies.append(f"{depart}-{arrivee}")
                break

        # Trouver et mettre à jour les arcs liés au point de départ
        for noeud in graphe:
            for i, (dest, val) in enumerate(graphe[noeud]):
                if dest == depart:
                    ancienne_valeur = graphe[noeud][i][1]
                    graphe[noeud][i] = (depart, valeur)
                    arcs_modifies.append(f"{noeud}-{depart}")

        # Trouver et mettre à jour les arcs liés au point d'arrivée
        if arrivee in graphe:
            for i, (dest, _) in enumerate(graphe[arrivee]):
                ancienne_valeur = graphe[arrivee][i][1]
                graphe[arrivee][i] = (dest, valeur)
                arcs_modifies.append(f"{arrivee}-{dest}")

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