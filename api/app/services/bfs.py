from collections import defaultdict, deque

def find_source_and_sink(edges):
    """
    Détermine automatiquement les nœuds source et puits du graphe.
    Source: nœud avec seulement des arêtes sortantes
    Puits: nœud avec seulement des arêtes entrantes
    """
    all_nodes = set()
    incoming = set()
    outgoing = set()
    
    for source, target, _ in edges:
        all_nodes.add(source)
        all_nodes.add(target)
        outgoing.add(source)
        incoming.add(target)
    
    # Source: nœud avec arêtes sortantes mais pas entrantes
    sources = outgoing - incoming
    # Puits: nœud avec arêtes entrantes mais pas sortantes  
    sinks = incoming - outgoing
    
    # Retourner le premier trouvé ou None
    source = next(iter(sources)) if sources else None
    sink = next(iter(sinks)) if sinks else None
    
    return source, sink

def pathThroughSpecificEdge(edges, specific_edge, satured_edges):
    """
    Trouve un chemin dans le graphe passant par un arc spécifique, en évitant les arcs saturés.
    
    :param edges: Liste de tuples (source, target, capacity).
    :param specific_edge: Arc spécifique (source, target, capacity) que le chemin doit contenir.
    :param satured_edges: Ensemble des arcs saturés (u, v, 0) à éviter.
    :return: Liste des arcs du chemin valide, ou None si aucun chemin n'existe.
    """
    graph = defaultdict(list)
    for source, target, capacity in edges:
        if (source, target, capacity) not in satured_edges:  
            graph[source].append((target, capacity))

    # Vérifier si l'arc spécifique est valide (et non saturé)
    if specific_edge in satured_edges:
        return None 
    if specific_edge[0] not in graph or specific_edge[1] not in [t[0] for t in graph[specific_edge[0]]]:
        return None  

    def bfs_path(source, target):
        queue = deque([(source, [])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            if current == target:
                return path
            if current not in visited:
                visited.add(current)
                for neighbor, capacity in graph[current]:
                    if neighbor not in visited:
                        new_edge = (current, neighbor, capacity)
                        if new_edge not in satured_edges:  # Éviter les arcs saturés
                            queue.append((neighbor, path + [new_edge]))
        return None

    # Déterminer automatiquement la source et le puits
    source_node, target_sink = find_source_and_sink(edges)
    
    if not source_node or not target_sink:
        return None  # Impossible de déterminer source/puits
    
    # Cas 1: L'arc spécifique part de la source → chercher chemin de sa cible au puits
    if specific_edge[0] == source_node:
        # Si l'arête va directement vers le puits, c'est le chemin complet
        if specific_edge[1] == target_sink:
            return [specific_edge]
        # Sinon, chercher un chemin de la cible vers le puits
        path_from_specific = bfs_path(specific_edge[1], target_sink)
        return [specific_edge] + path_from_specific if path_from_specific else None

    # Cas 2: L'arc spécifique arrive au puits → chercher chemin de la source à sa source
    elif specific_edge[1] == target_sink:
        path_to_specific = bfs_path(source_node, specific_edge[0])
        return path_to_specific + [specific_edge] if path_to_specific else None

    # Cas général: L'arc est au milieu → combiner deux BFS
    else:
        path_to_specific = bfs_path(source_node, specific_edge[0])
        if not path_to_specific:
            return None
        path_from_specific = bfs_path(specific_edge[1], target_sink)
        if not path_from_specific:
            return None
        return path_to_specific + [specific_edge] + path_from_specific