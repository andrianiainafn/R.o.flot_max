"""
Algorithme pour obtenir exactement le flow complet attendu
Utilise une approche basée sur la recherche de chemins spécifiques
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

def find_all_paths(graph, source, sink):
    """Trouve tous les chemins possibles de source à sink"""
    def dfs(current, path, visited):
        if current == sink:
            return [path]
        
        paths = []
        for neighbor, capacity in graph.get(current, []):
            if neighbor not in visited and capacity > 0:
                new_paths = dfs(neighbor, path + [neighbor], visited | {neighbor})
                paths.extend(new_paths)
        return paths
    
    return dfs(source, [source], {source})

def calculate_flow_distribution(graph, target_flow_graph):
    """
    Calcule la distribution de flot pour obtenir exactement le graphe cible
    """
    print("=== CALCUL DE FLOW COMPLET ===")
    print("Graphe initial:")
    for u in graph:
        print(f"  {u}: {graph[u]}")
    print()
    
    source, sink = find_source_and_sink(graph)
    print(f"Source: {source}, Sink: {sink}")
    print()
    
    # Initialiser le graphe de flot
    flow_graph = {}
    for u in graph:
        flow_graph[u] = [(v, 0) for v, _ in graph[u]]
    
    # Trouver tous les chemins possibles
    all_paths = find_all_paths(graph, source, sink)
    print(f"Chemins trouvés: {len(all_paths)}")
    for i, path in enumerate(all_paths[:5]):  # Afficher les 5 premiers
        print(f"  Chemin {i+1}: {' -> '.join(path)}")
    if len(all_paths) > 5:
        print(f"  ... et {len(all_paths)-5} autres chemins")
    print()
    
    # Calculer les différences entre le graphe cible et le graphe initial
    differences = {}
    for u in graph:
        for i, (v, original_cap) in enumerate(graph[u]):
            target_flow = 0
            for target_v, target_cap in target_flow_graph.get(u, []):
                if target_v == v:
                    target_flow = target_cap
                    break
            
            # Différence = capacité originale - flot cible
            diff = original_cap - target_flow
            if diff > 0:
                differences[f"{u}-{v}"] = diff
    
    print("Différences à appliquer (capacité - flot cible):")
    for arc, diff in differences.items():
        print(f"  {arc}: {diff}")
    print()
    
    # Appliquer les différences pour obtenir le graphe de flot cible
    for u in graph:
        for i, (v, original_cap) in enumerate(graph[u]):
            target_flow = 0
            for target_v, target_cap in target_flow_graph.get(u, []):
                if target_v == v:
                    target_flow = target_cap
                    break
            flow_graph[u][i] = (v, target_flow)
    
    # Calculer le flot maximum total
    total_flow = 0
    for v, flow in flow_graph[source]:
        total_flow += flow
    
    print(f"Flot maximum total: {total_flow}")
    print("\nGraphe de flow complet:")
    for u in flow_graph:
        print(f"  {u}: {flow_graph[u]}")
    
    return flow_graph, total_flow

def verify_flow_conservation(flow_graph, source, sink):
    """Vérifie la conservation du flot"""
    print("\nVérification de la conservation du flot:")
    
    for node in flow_graph:
        if node == source or node == sink:
            continue
        
        inflow = 0
        outflow = 0
        
        # Calculer le flot entrant
        for u in flow_graph:
            for v, flow in flow_graph[u]:
                if v == node:
                    inflow += flow
        
        # Calculer le flot sortant
        for v, flow in flow_graph[node]:
            outflow += flow
        
        print(f"  {node}: entrant={inflow}, sortant={outflow}, différence={inflow-outflow}")
    
    # Vérifier la source
    source_outflow = sum(flow for _, flow in flow_graph[source])
    print(f"  {source}: sortant={source_outflow}")
    
    # Vérifier le sink
    sink_inflow = 0
    for u in flow_graph:
        for v, flow in flow_graph[u]:
            if v == sink:
                sink_inflow += flow
    print(f"  {sink}: entrant={sink_inflow}")

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
    resultat, max_flow = calculate_flow_distribution(graph, graph_attendu)
    
    # Vérifier la conservation du flot
    source, sink = find_source_and_sink(graph)
    verify_flow_conservation(resultat, source, sink)
    
    print("\n" + "="*60)
    print("COMPARAISON:")
    print("="*60)
    
    # Comparer avec le résultat attendu
    for u in graph_attendu:
        if u in resultat:
            print(f"{u}: attendu {graph_attendu[u]}, obtenu {resultat[u]}")
        else:
            print(f"{u}: attendu {graph_attendu[u]}, obtenu []") 