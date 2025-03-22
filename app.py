from flask import Flask, request, jsonify
from flask_cors import CORS  # Importez cette bibliothèque

from flow_max import firstStep, makeTable, constructGraph

# Création de l'application Flask
app = Flask(__name__)
CORS(app)  # Activez CORS pour toute l'application

# Ou pour une route spécifique uniquement:
# CORS(app, resources={r"/flow-max": {"origins": "*"}})

@app.route('/flow-max', methods=['POST'])
def flow_max():
    try:
        # Récupérer les données du graphe à partir du corps de la requête
        data = request.json
        if not data or 'graph' not in data:
            return jsonify({'error': 'Le graphe est requis dans le corps de la requête'}), 400

        graph = data['graph']

        # Initialiser le graphe et créer la table
        init_graph = firstStep(graph)
        table = makeTable(graph)

        # Construire le graphe mis à jour
        graph_maj, table_maj = constructGraph(table, init_graph)

        # Préparer la réponse
        response = {
            'graph_final': graph_maj,
            'table_finale': table_maj,
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)