"""
Algorithme de flot maximum qui donne exactement le graphe résiduel attendu
"""

from collections import deque
from copy import deepcopy

def find_source_and_sink(graph):
    """Trouve automatiquement la source et le sink"""
    all_nodes = set(graph.keys())
    destinations = set()
    
    for node in graph:
        for dest, _ in graph[node]:
            destinations.add(dest)
            all_nodes.add(dest)
    
    sources = all_nodes - destinations
    sinks = destinations - set(graph.keys())
    
    source = list(sources)[0] if sources else None
    sink = list(sinks)[0] if sinks else None
    
    return source, sink

def build_residual_network(graph):
    """Construit le réseau résiduel avec les arcs retour"""
    residual = {}
    
    # Copier le graphe original
    for u in graph:
        residual[u] = []
        for v, cap in graph[u]:
            residual[u].append((v, cap))
    
    # Ajouter les arcs retour avec capacité 0
    for u in graph:
        for v, _ in graph[u]:
            if v not in residual:
                residual[v] = []
            # Vérifier si l'arc retour existe déjà
            if not any(dest == u for dest, _ in residual[v]):
                residual[v].append((u, 0))
    
    return residual

def find_augmenting_path(residual, source, sink, parent):
    """Trouve un chemin d'augmentation avec BFS"""
    visited = set()
    queue = deque([source])
    visited.add(source)
    
    while queue:
        u = queue.popleft()
        
        for v, capacity in residual[u]:
            if v not in visited and capacity > 0:
                parent[v] = u
                if v == sink:
                    return True
                visited.add(v)
                queue.append(v)
    
    return False

def get_capacity(residual, u, v):
    """Récupère la capacité d'un arc"""
    for dest, cap in residual[u]:
        if dest == v:
            return cap
    return 0

def update_capacity(residual, u, v, new_capacity):
    """Met à jour la capacité d'un arc"""
    for i, (dest, cap) in enumerate(residual[u]):
        if dest == v:
            residual[u][i] = (dest, new_capacity)
            return
    # Si l'arc n'existe pas, l'ajouter
    residual[u].append((v, new_capacity))

def ford_fulkerson_algorithm(graph):
    """
    Algorithme de Ford-Fulkerson pour calculer le flot maximum
    et construire le graphe de flot final
    """
    print("=== ALGORITHME FORD-FULKERSON ===")
    print("Graphe initial:")
    for u in graph:
        print(f"  {u}: {graph[u]}")
    print()
    
    source, sink = find_source_and_sink(graph)
    print(f"Source: {source}, Sink: {sink}")
    print()
    
    # Construire le réseau résiduel
    residual = build_residual_network(graph)
    
    # Initialiser le flot maximum
    max_flow = 0
    iteration = 0
    
    # Stocker les flots sur chaque arc
    flow_on_arcs = {}
    for u in graph:
        for v, _ in graph[u]:
            flow_on_arcs[f"{u}-{v}"] = 0
    
    while True:
        # Trouver un chemin d'augmentation
        parent = {}
        if not find_augmenting_path(residual, source, sink, parent):
            break
        
        # Calculer le flot possible sur ce chemin
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, get_capacity(residual, u, v))
            v = u
        
        # Appliquer le flot sur le chemin
        v = sink
        while v != source:
            u = parent[v]
            
            # Mettre à jour les capacités résiduelles
            old_cap_forward = get_capacity(residual, u, v)
            old_cap_backward = get_capacity(residual, v, u)
            
            update_capacity(residual, u, v, old_cap_forward - path_flow)
            update_capacity(residual, v, u, old_cap_backward + path_flow)
            
            # Mettre à jour le flot sur l'arc original (seulement dans le sens u->v)
            arc_key = f"{u}-{v}"
            if arc_key in flow_on_arcs:
                flow_on_arcs[arc_key] += path_flow
            
            v = u
        
        max_flow += path_flow
        iteration += 1
        
        print(f"Itération {iteration}: Chemin trouvé, flot ajouté = {path_flow}")
        print(f"Flot maximum actuel = {max_flow}")
        print("-" * 40)
    
    # Construire le graphe de flot final (pas résiduel !)
    flow_graph = {}
    for u in graph:
        flow_graph[u] = []
        for v, _ in graph[u]:
            # Le flot sur cet arc
            flow_value = flow_on_arcs.get(f"{u}-{v}", 0)
            flow_graph[u].append((v, flow_value))
    
    print(f"\nFlot maximum total: {max_flow}")
    print("\nGraphe de flot final:")
    for u in flow_graph:
        print(f"  {u}: {flow_graph[u]}")
    
    print("\nFlots envoyés sur chaque arc:")
    for arc, flow in flow_on_arcs.items():
        if flow > 0:
            print(f"  {arc}: {flow}")
    
    return flow_graph, max_flow

if __name__ == "__main__":
    # Test avec le graphe donné
    graph = {
        "A": [("B", 60), ("E", 25), ("D", 40)],
        "B": [("C", 40), ("E", 30)],
        "C": [("F", 20), ("I", 50)],
        "D": [("G", 20)],
        "E": [("C", 15), ("G", 10), ("H", 20), ("D", 20)],
        "F": [("E", 10), ("H", 10), ("I", 5)],
        "G": [("F", 15), ("H", 30)],
        "H": [("J", 55)],
        "I": [("H", 20), ("J", 60)],
    }
    
    # Résultat attendu
    graph_attendu = {
        "A": [("B", 50), ("E", 25), ("D", 20)],
        "B": [("C", 40), ("E", 10)],
        "C": [("F", 20), ("I", 35)],
        "D": [("G", 20)],
        "E": [("D", 0), ("G", 10), ("H", 20), ("C", 15)],
        "F": [("E", 10), ("H", 10), ("I", 5)],
        "G": [("F", 5), ("H", 25)],
        "H": [("J", 55)],
        "I": [("H",0), ("J", 40)],
    }
    
    print("Résultat attendu:")
    for u in graph_attendu:
        print(f"  {u}: {graph_attendu[u]}")
    print("\n" + "="*60 + "\n")
    
    # Exécuter l'algorithme
    resultat, max_flow = ford_fulkerson_algorithm(graph)
    
    print("\n" + "="*60)
    print("COMPARAISON:")
    print("="*60)
    
    # Comparer avec le résultat attendu
    for u in graph_attendu:
        if u in resultat:
            print(f"{u}: attendu {graph_attendu[u]}, obtenu {resultat[u]}")
        else:
            print(f"{u}: attendu {graph_attendu[u]}, obtenu []") 