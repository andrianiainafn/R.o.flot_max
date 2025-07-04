from app.services.findMinEdge import minEdge
from app.services.bfs import pathThroughSpecificEdge
from app.services.updateGraph import updateGraph, update_flow_graph
from app.services.mark import find_augmenting_path
from app.services.verifySaturedBlocked import finalSaturedEdge
from app.services.residual_table import create_residual_table_display

from collections import OrderedDict

def fordFulkerson(graphOriginal):
    graph = [(e["source"], e["target"], e["capacity"]) for e in graphOriginal]
    flow_graph = [(u, v, 0) for u, v, c in graph]
    residual_graph = graph.copy()

    satured_edges = set()
    blocked_edges = set()
    step_list = [{"type": "graph_update", "graph": list(flow_graph)}]
    marked_path_list = []
    max_flow = 0

    while True:
        available_edges = [e for e in residual_graph if e not in blocked_edges and e[2] > 0]
        if not available_edges:
            break

        min_e = minEdge(available_edges)
        if min_e is None:
            continue  # Skip if no edge found

        step_list.append({"type": "min_edge", "edge": list(min_e)})

        path = pathThroughSpecificEdge(residual_graph, min_e, satured_edges)
        if not path:
            blocked_edges.add(min_e)
            step_list.append({
                "type": "graph_update",
                "graph": list(flow_graph),
                "satured": list(satured_edges),
                "blocked": list(blocked_edges)
            })
            continue

        step_list.append({"type": "path_min", "path": list(path)})

        min_capacity = min_e[2]
        flow_graph, residual_graph = updateGraph(flow_graph, residual_graph, min_capacity, path)

        for u, v, c in path:
            for ru, rv, rc in residual_graph:
                if (ru, rv) == (u, v) and rc == 0:
                    satured_edges.add((u, v, 0))

        max_flow += min_capacity
        step_list.append({
            "type": "graph_update",
            "graph": list(flow_graph),
            "satured": list(satured_edges),
            "blocked": list(blocked_edges)
        })

    while True:
        marked_path = find_augmenting_path(flow_graph, satured_edges)
        if marked_path is None:
            break

        # Sauvegarder le graphe avant le marquage
        graph_before_marking = list(flow_graph)

        cap_back = [v for _, s, v in marked_path if s == '-']
        min_back = min(cap_back) if cap_back else 0
        max_flow += min_back

        flow_graph = update_flow_graph(marked_path, flow_graph, min_back)

        # Calculate node markings for THIS path only
        current_node_markings = {}
        for (u, v), sign, _ in marked_path:
            if u[0] not in current_node_markings:
                current_node_markings[u[0]] = sign
            if v[0] not in current_node_markings:
                current_node_markings[v[0]] = sign
                

        print("Mark-2 : ", current_node_markings)

        marked_path_list.append({
            "type": "marked_path",
            "path": [(u, s, c) for u, s, c in marked_path],
            "graph": list(flow_graph),
            "graph_before": graph_before_marking,
            "node_markings": current_node_markings
        })

        print("mark : ", marked_path)
        print("node_markings (current path): ", current_node_markings)

    # Ajouter le graphe avant marquage même si aucun chemin marqué n'est trouvé
    if not marked_path_list:
        marked_path_list.append({
            "type": "no_augmenting_path",
            "message": "Aucun chemin d'augmentation trouvé - le flot maximum est atteint",
            "graph_before": list(flow_graph),
            "graph": list(flow_graph)
        })

    final_satured = finalSaturedEdge(graph, flow_graph)

    # Créer le tableau résiduel pour l'affichage
    residual_table = create_residual_table_display(graphOriginal, step_list)

    return {
        "steps": step_list,
        "marked_paths": marked_path_list,  # Contains node_markings for each path
        "residual_table": residual_table,
        "final": {
            "max_flow": max_flow,
            "final_flow": list(flow_graph),
            "final_satured": list(final_satured),
            "blocked_edges": list(blocked_edges)
        }
    }