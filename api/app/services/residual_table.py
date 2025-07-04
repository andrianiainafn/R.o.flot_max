def make_residual_table(graph):
    """
    Crée un tableau résiduel pour le graphe donné.
    """
    # Convertir le graphe au format dictionnaire si c'est une liste
    if isinstance(graph, list):
        graph_dict = {}
        for edge in graph:
            source = edge["source"]
            target = edge["target"]
            capacity = edge["capacity"]
            
            if source not in graph_dict:
                graph_dict[source] = []
            graph_dict[source].append((target, capacity))
        graph = graph_dict
    
    nodes = list(graph.keys())
    table = {}

    for node in graph:
        for edge, distance in graph[node]:
            key = f"{node}-{edge}"
            table[key] = [distance] + [0] * len(nodes)

    return table

def update_residual_table_for_step(table, step_index, min_flow, modified_edges, original_graph):
    """
    Met à jour le tableau résiduel pour une étape donnée.
    """
    # Copier le tableau pour éviter de modifier l'original
    updated_table = {}
    for key, values in table.items():
        updated_table[key] = values.copy()
    
    # S'assurer que toutes les colonnes ont la bonne longueur
    for key, values in updated_table.items():
        while len(values) <= step_index:
            values.append(values[step_index - 1] if step_index > 0 else values[0])
    
    # Mettre à jour les valeurs pour les arêtes modifiées
    for key, values in updated_table.items():
        if key in modified_edges:
            # Calculer la nouvelle valeur
            previous_value = values[step_index - 1] if step_index > 0 else values[0]
            if isinstance(previous_value, (int, float)) and previous_value > 0:
                new_value = previous_value - min_flow
                values[step_index] = new_value
                
                # Si la nouvelle valeur est 0, marquer comme 'S' (saturé)
                if new_value == 0:
                    for i in range(step_index, len(values)):
                        values[i] = 'S'
            else:
                values[step_index] = previous_value
        else:
            # Si l'arête n'est pas modifiée, conserver la valeur précédente
            if step_index > 0:
                values[step_index] = values[step_index - 1]
    
    return updated_table

def create_residual_table_display(graph, steps):
    """
    Crée un tableau résiduel complet pour l'affichage.
    """
    # Initialiser le tableau avec les capacités initiales
    residual_table = {}
    for edge in graph:
        source = edge["source"]
        target = edge["target"]
        capacity = edge["capacity"]
        key = f"{source}-{target}"
        residual_table[key] = [capacity]
    
    # Ajouter les colonnes pour chaque étape
    for i, step in enumerate(steps):
        if step["type"] == "graph_update":
            # Pour cette étape, on peut calculer les valeurs résiduelles
            current_flow = step["graph"]
            
            # Mettre à jour le tableau pour cette étape
            for key in residual_table:
                # Trouver la valeur actuelle dans le graphe de flot
                source, target = key.split("-")
                current_value = 0
                
                # Chercher dans le graphe de flot actuel
                for u, v, flow in current_flow:
                    if u == source and v == target:
                        # Calculer la valeur résiduelle (capacité - flot)
                        original_capacity = 0
                        for edge in graph:
                            if edge["source"] == source and edge["target"] == target:
                                original_capacity = edge["capacity"]
                                break
                        current_value = original_capacity - flow
                        break
                
                residual_table[key].append(current_value)
                
                # Marquer comme saturé si la valeur est 0
                if current_value == 0 and len(residual_table[key]) > 1:
                    residual_table[key][-1] = 'S'
                
                # Marquer comme bloqué si l'arête est dans la liste des arêtes bloquées
                if "blocked" in step and any(f"{u}-{v}" == key for u, v, _ in step["blocked"]):
                    residual_table[key][-1] = 'B'
    
    return residual_table 