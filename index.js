// Script pour l'interface de construction de graphe
document.addEventListener('DOMContentLoaded', function() {
  // Structure pour stocker le graphe
  let graph = {};

  // Référence à l'instance du réseau
  let network;

  // Collections pour les nœuds et les arêtes
  const nodes = new vis.DataSet();
  const edges = new vis.DataSet();

  // Initialisation du réseau
  function initNetwork() {
    const container = document.getElementById('graph-container');
    const data = { nodes, edges };
    const options = {
      physics: {
        enabled: true,
        stabilization: true,
        solver: 'forceAtlas2Based'
      },
      edges: {
        arrows: {
          to: { enabled: true, scaleFactor: 1 }
        },
        font: {
          align: 'middle'
        }
      },
      manipulation: {
        enabled: true,
        addNode: function(nodeData, callback) {
          document.getElementById('node-operation').textContent = 'Ajouter un nœud';
          document.getElementById('node-modal').style.display = 'block';
          document.getElementById('node-saveButton').onclick = saveNodeData.bind(null, nodeData, callback);
        },
        addEdge: function(edgeData, callback) {
          document.getElementById('edge-operation').textContent = 'Ajouter une arête';
          document.getElementById('edge-modal').style.display = 'block';
          document.getElementById('edge-saveButton').onclick = saveEdgeData.bind(null, edgeData, callback);
        },
        deleteNode: function(nodeData, callback) {
          deleteNode(nodeData.nodes[0]);
          callback(nodeData);
        },
        deleteEdge: function(edgeData, callback) {
          deleteEdge(edgeData.edges[0]);
          callback(edgeData);
        }
      }
    };

    network = new vis.Network(container, data, options);
    updateGraphOutput();
  }

  // Fonction pour enregistrer les données d'un nœud
  function saveNodeData(nodeData, callback) {
    const nodeId = document.getElementById('node-id').value;
    if (!nodeId) {
      alert('Veuillez entrer un ID pour le nœud');
      return;
    }

    nodeData.id = nodeId;
    nodeData.label = nodeId;

    // Ajouter au graphe
    if (!graph[nodeId]) {
      graph[nodeId] = [];
    }

    // Fermer la modal et appeler le callback
    document.getElementById('node-modal').style.display = 'none';
    document.getElementById('node-id').value = '';
    callback(nodeData);
    updateGraphOutput();
  }

  // Fonction pour enregistrer les données d'une arête
  function saveEdgeData(edgeData, callback) {
    const weight = parseInt(document.getElementById('edge-weight').value);
    if (isNaN(weight)) {
      alert('Veuillez entrer un poids (nombre) valide');
      return;
    }

    edgeData.label = weight.toString();

    // Ajouter au graphe
    if (!graph[edgeData.from]) {
      graph[edgeData.from] = [];
    }
    graph[edgeData.from].push([edgeData.to, weight]);

    // Fermer la modal et appeler le callback
    document.getElementById('edge-modal').style.display = 'none';
    document.getElementById('edge-weight').value = '';
    callback(edgeData);
    updateGraphOutput();
  }

  // Fonction pour supprimer un nœud
  function deleteNode(nodeId) {
    // Supprimer le nœud du graphe
    delete graph[nodeId];

    // Supprimer les connexions qui le mentionnent
    for (const source in graph) {
      graph[source] = graph[source].filter(([target, _]) => target !== nodeId);
    }

    updateGraphOutput();
  }

  // Fonction pour supprimer une arête
  function deleteEdge(edgeId) {
    const edge = edges.get(edgeId);
    if (edge && graph[edge.from]) {
      graph[edge.from] = graph[edge.from].filter(([target, weight]) =>
        !(target === edge.to && weight.toString() === edge.label)
      );
    }

    updateGraphOutput();
  }

  // Fonction pour mettre à jour l'affichage du graphe
  function updateGraphOutput() {
    const outputElement = document.getElementById('graph-output');
    outputElement.textContent = 'graph = {\n';

    for (const source in graph) {
      if (graph[source].length > 0) {
        outputElement.textContent += `    "${source}": [`;
        graph[source].forEach(([target, weight], index) => {
          outputElement.textContent += `("${target}", ${weight})`;
          if (index < graph[source].length - 1) {
            outputElement.textContent += ', ';
          }
        });
        outputElement.textContent += '],\n';
      }
    }

    outputElement.textContent += '}';
  }

  // Initialisation de l'interface
  initNetwork();

  // Gestion des modales
  document.querySelectorAll('.close-modal').forEach(button => {
    button.addEventListener('click', function() {
      this.closest('.modal').style.display = 'none';
    });
  });

  // Bouton pour exporter le graphe
  document.getElementById('export-btn').addEventListener('click', function() {
    const graphOutput = document.getElementById('graph-output').textContent;
    const blob = new Blob([graphOutput], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'graph-data.py';
    a.click();
    URL.revokeObjectURL(url);
  });

  // Bouton pour réinitialiser le graphe
  document.getElementById('reset-btn').addEventListener('click', function() {
    if (confirm('Êtes-vous sûr de vouloir réinitialiser le graphe?')) {
      graph = {};
      nodes.clear();
      edges.clear();
      updateGraphOutput();
    }
  });

  // Bouton pour ajouter un exemple de graphe
  document.getElementById('example-btn').addEventListener('click', function() {
    if (confirm('Êtes-vous sûr de vouloir charger l\'exemple de graphe? Cela effacera votre graphe actuel.')) {
      graph = {
        "alfa": [["A", 45], ["B", 25], ["C", 30]],
        "A": [["D", 10], ["E", 15], ["G", 20]],
        "B": [["D", 20], ["E", 5], ["F", 15]],
        "C": [["F", 10], ["G", 15]],
        "D": [["omega", 30]],
        "E": [["omega", 10]],
        "F": [["omega", 20]],
        "G": [["omega", 40]]
      };

      // Recréer le réseau avec les nouvelles données
      nodes.clear();
      edges.clear();

      // Ajouter les nœuds
      const nodeIds = new Set();
      for (const source in graph) {
        if (!nodeIds.has(source)) {
          nodeIds.add(source);
          nodes.add({id: source, label: source});
        }

        graph[source].forEach(([target, _]) => {
          if (!nodeIds.has(target)) {
            nodeIds.add(target);
            nodes.add({id: target, label: target});
          }
        });
      }

      // Ajouter les arêtes
      for (const source in graph) {
        graph[source].forEach(([target, weight]) => {
          edges.add({
            from: source,
            to: target,
            label: weight.toString()
          });
        });
      }

      updateGraphOutput();
    }
  });
});