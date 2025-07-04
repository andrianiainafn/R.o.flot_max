def find_source_and_sink_from_flow(flow):
    """
    Détermine automatiquement les nœuds source et puits à partir du graphe de flot.
    """
    all_nodes = set()
    incoming = set()
    outgoing = set()
    
    for source, target, _ in flow:
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

def find_augmenting_path(flow, saturated_edges):
    from collections import defaultdict

    graph = defaultdict(list)
    flow_dict = {}

    for u, v, f in flow:
        graph[u].append(v)
        graph[v].append(u) 
        flow_dict[(u, v)] = f

    visited = set()
    
    # Déterminer automatiquement la source et le puits
    source_node, sink_node = find_source_and_sink_from_flow(flow)
    
    if not source_node or not sink_node:
        return None  # Impossible de déterminer source/puits

    def dfs(node, path):
        if node == sink_node:
            return path

        visited.add(node)

        for neighbor in graph[node]:
            if any(u == node and v == neighbor for (u, v, f) in saturated_edges):
                continue
            if neighbor not in visited and flow_dict.get((node, neighbor), 0) > 0:
                res = dfs(neighbor, path + [((node, neighbor), '+', flow_dict[(node, neighbor)])])
                if res:
                    return res

        for neighbor in graph[node]:
            if (neighbor, node) in flow_dict and flow_dict[(neighbor, node)] > 0:
                if neighbor not in visited:
                    res = dfs(neighbor, path + [((neighbor, node), '-', flow_dict[(neighbor, node)])])
                    if res:
                        return res

        return None

    # Utiliser la source détectée automatiquement
    return dfs(source_node, [])