from collections import defaultdict, deque
from flask import Flask, request, jsonify
from flask_cors import CORS

from flow_max import firstStep, makeTable, constructGraph


class Graph:
    def __init__(self, graph):
        self.graph = graph
        self.flow = defaultdict(lambda: defaultdict(int))
        self.residual_capacity = defaultdict(lambda: defaultdict(int))
        self.initialize_residual_graph()

    def initialize_residual_graph(self):
        """Initialise le graphe résiduel avec les capacités originales"""
        # Initialiser toutes les capacités résiduelles
        for u in self.graph:
            for v, capacity in self.graph[u]:
                # Capacité résiduelle forward = capacité originale
                self.residual_capacity[u][v] = capacity
                # Capacité résiduelle backward = 0 initialement
                self.residual_capacity[v][u] = 0

    def find_augmenting_path_dfs(self, source, sink, visited=None, path=None):
        """
        Trouve un chemin augmentant en utilisant DFS
        Retourne (chemin, capacité_minimale) ou (None, 0) si aucun chemin
        """
        if visited is None:
            visited = set()
        if path is None:
            path = []

        visited.add(source)
        path.append(source)

        # Si on atteint le sink, retourner le chemin et calculer la capacité min
        if source == sink:
            min_capacity = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                min_capacity = min(min_capacity, self.residual_capacity[u][v])
            return path.copy(), min_capacity

        # Explorer tous les voisins avec capacité résiduelle > 0
        for v in self.residual_capacity[source]:
            if v not in visited and self.residual_capacity[source][v] > 0:
                result_path, min_cap = self.find_augmenting_path_dfs(v, sink, visited, path)
                if result_path:
                    return result_path, min_cap

        # Backtrack
        path.pop()
        return None, 0

    def update_residual_graph(self, path, flow_value):
        """Met à jour le graphe résiduel après avoir trouvé un chemin augmentant"""
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]

            # Mettre à jour le flot réel (seulement pour les arcs originaux)
            if v in dict(self.graph.get(u, [])):
                self.flow[u][v] += flow_value
            else:
                # Arc backward - diminuer le flot de l'arc original
                self.flow[v][u] -= flow_value

            # Mettre à jour les capacités résiduelles
            self.residual_capacity[u][v] -= flow_value  # Réduire capacité forward
            self.residual_capacity[v][u] += flow_value  # Augmenter capacité backward

    def get_flow_details(self):
        """Retourne les détails du flot pour la réponse API"""
        flow_details = {}
        for u in self.graph:
            flow_details[u] = {}
            for v, capacity in self.graph[u]:
                current_flow = self.flow[u][v]
                flow_details[u][v] = {
                    'flow': current_flow,
                    'capacity': capacity,
                    'utilization': f"{current_flow}/{capacity}"
                }
        return flow_details

    def print_flow(self):
        """Méthode pour debug - affiche le flot actuel"""
        print("Flot actuel:")
        for u in self.graph:
            for v, capacity in self.graph[u]:
                current_flow = self.flow[u][v]
                print(f"  {u} -> {v}: {current_flow}/{capacity}")
        print()

    def print_residual_graph(self):
        """Affiche le graphe résiduel pour debug"""
        print("Graphe résiduel:")
        for u in self.residual_capacity:
            for v in self.residual_capacity[u]:
                if self.residual_capacity[u][v] > 0:
                    print(f"  {u} -> {v}: {self.residual_capacity[u][v]}")
        print()

    def ford_fulkerson(self, source, sink):
        """
        Algorithme Ford-Fulkerson avec recherche DFS
        """
        iterations = []
        iteration_count = 0
        max_flow = 0

        print(f"=== Début Ford-Fulkerson ===")
        print(f"Source: {source}, Sink: {sink}")
        print()

        while True:
            # Chercher un chemin augmentant
            path, flow_value = self.find_augmenting_path_dfs(source, sink)

            # Si aucun chemin augmentant, on a terminé
            if path is None:
                print("Aucun chemin augmentant trouvé. Algorithme terminé.")
                break

            iteration_count += 1
            max_flow += flow_value

            print(f"--- Itération {iteration_count} ---")
            print(f"Chemin augmentant: {' -> '.join(path)}")
            print(f"Capacité résiduelle minimale: {flow_value}")
            print(f"Flot total jusqu'à présent: {max_flow}")

            # Mettre à jour le graphe résiduel
            self.update_residual_graph(path, flow_value)

            # Afficher l'état pour debug
            self.print_flow()

            # Sauvegarder les détails de l'itération
            iterations.append({
                'iteration': iteration_count,
                'augmenting_path': path,
                'flow_value': flow_value,
                'total_flow_so_far': max_flow
            })

        print(f"=== Résultat final ===")
        print(f"Flot maximum: {max_flow}")
        self.print_flow()

        return {
            'max_flow': max_flow,
            'iterations': iterations,
            'flow_details': self.get_flow_details()
        }


# Création de l'application Flask
app = Flask(__name__)
CORS(app)


def detecter_source_et_sink(graph):
    """
    Détecte automatiquement la source (pas d'arcs entrants) et le sink (pas d'arcs sortants)
    """
    tous_noeuds = set(graph.keys())
    noeuds_avec_entrees = set()

    # Trouver tous les nœuds qui ont des arcs entrants
    for noeud in graph:
        for voisin, _ in graph[noeud]:
            noeuds_avec_entrees.add(voisin)
            tous_noeuds.add(voisin)

    # Source : nœud sans arcs entrants
    sources_possibles = tous_noeuds - noeuds_avec_entrees

    # Sink : nœud sans arcs sortants (pas dans les clés du graphe ou liste vide)
    sinks_possibles = set()
    for noeud in tous_noeuds:
        if noeud not in graph or len(graph[noeud]) == 0:
            sinks_possibles.add(noeud)

    # Retourner la première source et le premier sink trouvés
    source = list(sources_possibles)[0] if sources_possibles else None
    sink = list(sinks_possibles)[0] if sinks_possibles else None

    return source, sink


@app.route('/flow-max', methods=['POST'])
def flow_max():
    try:
        # Récupérer les données du graphe à partir du corps de la requête
        data = request.json
        if not data or 'graph' not in data:
            return jsonify({'error': 'Le graphe est requis dans le corps de la requête'}), 400

        graph = data['graph']

        # Détection automatique si pas spécifié
        if 'source' not in data or 'sink' not in data:
            auto_source, auto_sink = detecter_source_et_sink(graph)
            source = data.get('source', auto_source)
            sink = data.get('sink', auto_sink)
        else:
            source = data['source']
            sink = data['sink']

        # Vérifier que source et sink sont valides
        if source is None or sink is None:
            return jsonify({'error': 'Impossible de détecter la source et/ou le sink automatiquement'}), 400

        # Étapes existantes
        init_graph = firstStep(graph)
        table = makeTable(graph)
        graph_maj, table_maj = constructGraph(table, init_graph)

        # Nouvelle fonctionnalité : Calcul du flot maximum
        # Créer l'objet Graph pour Ford-Fulkerson
        ff_graph = Graph(graph)
        ford_fulkerson_result = ff_graph.ford_fulkerson(source, sink)

        # Préparer la réponse complète
        response = {
            'graph_final': graph_maj,
            'table_finale': table_maj,
            'ford_fulkerson': {
                'source': source,
                'sink': sink,
                'max_flow': ford_fulkerson_result['max_flow'],
                'iterations': ford_fulkerson_result['iterations'],
                'flow_details': ford_fulkerson_result['flow_details'],
                'total_iterations': len(ford_fulkerson_result['iterations'])
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Test avec votre exemple
if __name__ == '__main__':
    # Test local avec votre graphe
    test_graph = {
        "test": [("A", 45), ("B", 25), ("C", 30)],
        "A": [("D", 10), ("E", 15), ("G", 20)],
        "B": [("D", 20), ("E", 5), ("F", 15)],
        "C": [("F", 10), ("G", 15)],
        "D": [("omega", 30)],
        "E": [("omega", 10)],
        "F": [("omega", 20)],
        "G": [("omega", 40)],
    }

    print("Test avec le graphe fourni:")
    ff_graph = Graph(test_graph)
    result = ff_graph.ford_fulkerson("test", "omega")
    print(f"\nFlot maximum calculé: {result['max_flow']}")

    app.run(debug=True)