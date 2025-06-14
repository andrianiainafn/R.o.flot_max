from collections import defaultdict, deque
from flask import Flask, request, jsonify
from flask_cors import CORS

from flow_max import firstStep, makeTable, constructGraph


class Graph:
    def __init__(self, graph):
        self.graph = graph
        self.flow = defaultdict(dict)
        self.residual = defaultdict(dict)
        self.initialize_flow_and_residual()

    def initialize_flow_and_residual(self):
        for u in self.graph:
            for v, capacity in self.graph[u]:
                self.flow[u][v] = 0
                self.residual[u][v] = capacity
                if v not in self.residual:
                    self.residual[v] = {}
                self.residual[v][u] = 0

    def mark_nodes(self, source, sink):
        # Step 1: Mark nodes
        marked = set()
        marked.add(source)
        queue = deque()
        queue.append(source)
        parent = {}  # To store the path

        while queue:
            u = queue.popleft()
            for v, capacity in self.residual[u].items():
                if capacity > 0 and v not in marked:  # Non-saturated arc
                    marked.add(v)
                    queue.append(v)
                    parent[v] = u
            for v in self.flow:
                if self.flow[v].get(u, 0) > 0 and u not in marked:  # Non-zero flow
                    marked.add(u)
                    queue.append(u)
                    parent[u] = v

        return marked, parent

    def improve_flow(self, source, sink):
        # Step 2: Improve flow
        marked, parent = self.mark_nodes(source, sink)
        if sink not in marked:
            return False, None, 0  # No augmenting path

        # Find the augmenting path
        path = []
        v = sink
        while v != source:
            path.append(v)
            v = parent[v]
        path.append(source)
        path.reverse()

        # Find the minimum residual capacity along the path
        min_residual = float('inf')
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            if v in self.residual[u]:
                min_residual = min(min_residual, self.residual[u][v])
            else:
                min_residual = min(min_residual, self.flow[v][u])

        # Augment the flow along the path
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            if v in self.residual[u]:  # Forward arc
                self.flow[u][v] += min_residual
                self.residual[u][v] -= min_residual
                self.residual[v][u] += min_residual
            else:  # Backward arc
                self.flow[v][u] -= min_residual
                self.residual[v][u] += min_residual
                self.residual[u][v] -= min_residual

        print(f"Augmenting path: {path} with flow {min_residual}")
        self.print_flow()
        return True, path, min_residual

    def get_flow_details(self):
        """Retourne les détails du flot pour la réponse API"""
        flow_details = {}
        for u in self.graph:
            flow_details[u] = {}
            for v, capacity in self.graph[u]:
                current_flow = self.flow[u].get(v, 0)
                flow_details[u][v] = {
                    'flow': current_flow,
                    'capacity': capacity,
                    'utilization': f"{current_flow}/{capacity}"
                }
        return flow_details

    def print_flow(self):
        print("Current Flow:")
        for u in self.graph:
            for v, _ in self.graph[u]:
                print(f"{u} -> {v}: {self.flow[u][v]}/{self.residual[u][v] + self.flow[u][v]}")
        print()

    def ford_fulkerson(self, source, sink):
        """Algorithme Ford-Fulkerson avec retour des détails pour l'API"""
        iterations = []
        iteration_count = 0

        print("Step 1: Marking Nodes and Improving Flow")
        while True:
            improved, path, flow_value = self.improve_flow(source, sink)

            if not improved:
                break

            iteration_count += 1
            iterations.append({
                'iteration': iteration_count,
                'augmenting_path': path,
                'flow_value': flow_value
            })

        print("Final Maximum Flow:")
        self.print_flow()

        # Calculer le flot maximum
        max_flow = 0
        for v, _ in self.graph[source]:
            max_flow += self.flow[source][v]

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


if __name__ == '__main__':
    app.run(debug=True)