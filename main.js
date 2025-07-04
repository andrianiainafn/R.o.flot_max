document.addEventListener('DOMContentLoaded', function() {
  // Structure pour stocker le graphe
  let graph = {};

  // Référence à l'instance du réseau
  let network;

  // Collections pour les nœuds et les arêtes
  const nodes = new vis.DataSet();
  const edges = new vis.DataSet();

  // URL du service RO-Service
  const RO_SERVICE_URL = 'http://localhost:4321';

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

  // Fonction pour convertir le graphe au format attendu par le service RO
  function convertGraphToServiceFormat() {
    const serviceGraph = [];
    for (const source in graph) {
      graph[source].forEach(([target, capacity]) => {
        serviceGraph.push({
          source: source,
          target: target,
          capacity: capacity
        });
      });
    }
    return serviceGraph;
  }

  // Fonction pour créer un graphe de flot final
  function createFlowGraph(finalFlow, originalGraph) {
    // Créer un dictionnaire pour accéder rapidement aux flots
    const flowDict = {};
    finalFlow.forEach(([u, v, flow]) => {
      flowDict[`${u}-${v}`] = flow;
    });

    // Créer le graphe de flot final
    const flowGraph = {};
    for (const source in originalGraph) {
      flowGraph[source] = [];
      originalGraph[source].forEach(([target, capacity]) => {
        const flow = flowDict[`${source}-${target}`] || 0;
        flowGraph[source].push([target, flow]);
      });
    }

    return flowGraph;
  }

  // Fonction pour trouver automatiquement le nœud source
  function findSourceNode(flowGraph) {
    const allNodes = new Set();
    const hasIncoming = new Set();
    const hasOutgoing = new Set();
    
    for (const source in flowGraph) {
      allNodes.add(source);
      hasOutgoing.add(source);
      flowGraph[source].forEach(([target, _]) => {
        allNodes.add(target);
        hasIncoming.add(target);
      });
    }
    
    // Source: nœud avec arêtes sortantes mais pas entrantes
    const sources = [...hasOutgoing].filter(node => !hasIncoming.has(node));
    return sources.length > 0 ? sources[0] : null;
  }
  
  // Fonction pour trouver automatiquement le nœud puits
  function findSinkNode(flowGraph) {
    const allNodes = new Set();
    const hasIncoming = new Set();
    const hasOutgoing = new Set();
    
    for (const source in flowGraph) {
      allNodes.add(source);
      hasOutgoing.add(source);
      flowGraph[source].forEach(([target, _]) => {
        allNodes.add(target);
        hasIncoming.add(target);
      });
    }
    
    // Puits: nœud avec arêtes entrantes mais pas sortantes
    const sinks = [...hasIncoming].filter(node => !hasOutgoing.has(node));
    return sinks.length > 0 ? sinks[0] : null;
  }

  // Fonction pour afficher le graphe de flot final avec vis.js
  function displayFlowGraph(finalFlow, originalGraph, blockedEdges = []) {
    // Créer le graphe de flot final
    const flowGraph = createFlowGraph(finalFlow, originalGraph);
    
    // Déterminer automatiquement la source et le puits une seule fois
    const sourceNode = findSourceNode(flowGraph);
    const sinkNode = findSinkNode(flowGraph);
    
    // Créer un nouveau conteneur pour le graphe de flot
    const flowContainer = document.createElement('div');
    flowContainer.id = 'flow-graph-container';
    flowContainer.style.width = '100%';
    flowContainer.style.height = '400px';
    flowContainer.style.border = '1px solid #ddd';
    flowContainer.style.marginTop = '20px';
    flowContainer.style.backgroundColor = '#fafafa';

    // Créer les collections pour les nœuds et arêtes du graphe de flot
    const flowNodes = new vis.DataSet();
    const flowEdges = new vis.DataSet();

    // Ajouter les nœuds
    const nodeIds = new Set();
    for (const source in flowGraph) {
      if (!nodeIds.has(source)) {
        nodeIds.add(source);
        // Colorer différemment la source et le puits
        let color = '#97C2FC';
        if (source === sourceNode) color = '#FB7E81'; // Rouge pour la source
        if (source === sinkNode) color = '#7BE141'; // Vert pour le puits
        
        flowNodes.add({
          id: source, 
          label: source,
          color: color,
          font: { size: 16, weight: 'bold' }
        });
      }

      flowGraph[source].forEach(([target, flow]) => {
        if (!nodeIds.has(target)) {
          nodeIds.add(target);
          let color = '#97C2FC';
          if (target === sourceNode) color = '#FB7E81';
          if (target === sinkNode) color = '#7BE141';
          
          flowNodes.add({
            id: target, 
            label: target,
            color: color,
            font: { size: 16, weight: 'bold' }
          });
        }
      });
    }

    // Ajouter les arêtes avec les flots
    for (const source in flowGraph) {
      flowGraph[source].forEach(([target, flow]) => {
        // Trouver la capacité originale pour l'affichage
        let originalCapacity = 0;
        if (originalGraph[source]) {
          const originalEdge = originalGraph[source].find(([t, _]) => t === target);
          if (originalEdge) {
            originalCapacity = originalEdge[1];
          }
        }

        // Déterminer la couleur de l'arête basée sur le flot
        let edgeColor = '#E0E0E0'; // Gris par défaut (flot nul)
        
        if (flow === originalCapacity && flow > 0) {
          edgeColor = '#FF0000'; // Rouge pour arête saturée (flot = capacité)
        } else if (flow > 0 && flow < originalCapacity) {
          edgeColor = '#1976D2'; // Bleu pour arête avec flot partiel (flot < capacité)
        }

        flowEdges.add({
          from: source,
          to: target,
          label: `${flow}/${originalCapacity}`,
          color: {
            color: edgeColor,
            highlight: edgeColor,
            hover: edgeColor
          },
          width: 2 + (flow / originalCapacity) * 3, // Épaisseur proportionnelle au flot
          font: { size: 12, color: '#333' }
        });
      });
    }

    // Options pour le réseau de flot
    const flowOptions = {
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
        },
        chosen: false // Empêche le changement de couleur au survol
      },
      manipulation: {
        enabled: false // Désactiver la manipulation pour le graphe de flot
      }
    };

    // Créer le réseau de flot
    const flowNetwork = new vis.Network(flowContainer, { nodes: flowNodes, edges: flowEdges }, flowOptions);
    
    return flowContainer;
  }

  // Fonction pour afficher les résultats du calcul
  function displayResults(data) {
    const resultsSection = document.getElementById('results-section');
    const resultsContent = document.getElementById('results-content');
    
    let html = '<div class="results-container">';
    
    // Affichage du flot maximum
    html += `<div class="result-item">
      <h3>Flot Maximum : ${data.final.max_flow}</h3>
    </div>`;
    
    // Affichage des étapes
    if (data.steps && data.steps.length > 0) {
      html += '<div class="result-item">';
      html += '<h3>Étapes du calcul :</h3>';
      html += '<div class="steps-container">';
      data.steps.forEach((step, index) => {
        html += `<div class="step">
          <strong>Étape ${index + 1} :</strong> ${step.type}
          ${step.edge ? ` - Arête: (${step.edge[0]}, ${step.edge[1]}, ${step.edge[2]})` : ''}
          ${step.path ? ` - Chemin: ${JSON.stringify(step.path)}` : ''}
        </div>`;
      });
      html += '</div></div>';
    }
    
    // Affichage du tableau résiduel
    if (data.residual_table) {
      html += '<div class="result-item">';
      html += '<h3>Tableau résiduel :</h3>';
      html += '<div class="residual-table-container">';
      html += '<table class="residual-table">';
      
      // En-têtes du tableau
      html += '<thead><tr>';
      html += '<th>Arête</th>';
      html += '<th>Capacité initiale</th>';
      
      // Compter le nombre maximum d'étapes
      let maxSteps = 0;
      for (const edge in data.residual_table) {
        maxSteps = Math.max(maxSteps, data.residual_table[edge].length);
      }
      
      // Ajouter les en-têtes des étapes
      for (let i = 1; i < maxSteps; i++) {
        html += `<th>Étape ${i}</th>`;
      }
      html += '</tr></thead>';
      
      // Corps du tableau
      html += '<tbody>';
      for (const edge in data.residual_table) {
        html += '<tr>';
        html += `<td class="edge-name">${edge}</td>`;
        
        const values = data.residual_table[edge];
        for (let i = 0; i < maxSteps; i++) {
          const value = i < values.length ? values[i] : '';
          let cellClass = '';
          let displayValue = value;
          
          if (value === 'S') {
            cellClass = 'saturated';
            displayValue = 'S';
          } else if (value === 'B') {
            cellClass = 'blocked';
            displayValue = 'B';
          } else if (value === 0) {
            cellClass = 'zero';
          }
          
          html += `<td class="${cellClass}">${displayValue}</td>`;
        }
        html += '</tr>';
      }
      html += '</tbody></table>';
      
      // Légende
      html += '<div class="table-legend">';
      html += '<h4>Légende :</h4>';
      html += '<ul>';
      html += '<li><span class="saturated">S</span> : Arête saturée</li>';
      html += '<li><span class="blocked">B</span> : Arête bloquée</li>';
      html += '<li><span class="zero">0</span> : Capacité résiduelle nulle</li>';
      html += '</ul>';
      html += '</div>';
      html += '</div></div>';
    }
    
    // Affichage des chemins marqués avec graphes avant/après
    if (data.marked_paths && data.marked_paths.length > 0) {
      html += '<div class="result-item">';
      html += '<h3>Chemins d\'augmentation :</h3>';
      html += '<div class="paths-container">';
      data.marked_paths.forEach((pathData, index) => {
        html += `<div class="path">
          <strong>Chemin ${index + 1} :</strong>
          <div>Marquages des nœuds: ${JSON.stringify(pathData.node_markings)}</div>
          <div class="graphs-comparison">
            <div class="graph-before">
              <h4>Graphe avant le marquage :</h4>
              <div id="graph-before-${index}"></div>
            </div>
            <div class="graph-after">
              <h4>Graphe après le marquage :</h4>
              <div id="graph-after-${index}"></div>
            </div>
          </div>
        </div>`;
      });
      html += '</div></div>';
    }
    
    // Affichage du graphe de flot final
    if (data.final.final_flow) {
      html += '<div class="result-item">';
      html += '<h3>Graphe de flot final :</h3>';
      html += '<div id="flow-graph-placeholder"></div>';
      html += '<div class="flow-legend">';
      html += '<h4>Légende :</h4>';
      html += '<ul>';
      html += '<li><span style="color: #FB7E81;">🔴</span> Source</li>';
      html += '<li><span style="color: #7BE141;">🟢</span> Puits</li>';
      html += '<li><span style="color: #FF0000;">🔴</span> Arête saturée (flot = capacité)</li>';
      html += '<li><span style="color: #1976D2;">🔵</span> Arête avec flot partiel</li>';
      html += '<li><span style="color: #E0E0E0;">⚪</span> Arête sans flot</li>';
      html += '</ul>';
      html += '</div>';
      html += '</div>';
    }
    
    html += '</div>';
    
    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';

    // Afficher les graphes avant/après pour chaque chemin marqué
    if (data.marked_paths && data.marked_paths.length > 0) {
      data.marked_paths.forEach((pathData, index) => {
        // Graphe avant le marquage (utiliser le graphe original)
        const beforeContainer = document.getElementById(`graph-before-${index}`);
        if (beforeContainer && pathData.graph_before) {
          const beforeGraphContainer = displayFlowGraph(pathData.graph_before, graph, []);
          beforeContainer.appendChild(beforeGraphContainer);
        }
        
        // Graphe après le marquage
        const afterContainer = document.getElementById(`graph-after-${index}`);
        if (afterContainer && pathData.graph) {
          const afterGraphContainer = displayFlowGraph(pathData.graph, graph, []);
          afterContainer.appendChild(afterGraphContainer);
        }
      });
    }

    // Afficher le graphe de flot final après avoir créé le contenu HTML
    if (data.final.final_flow) {
      const placeholder = document.getElementById('flow-graph-placeholder');
      const flowGraphContainer = displayFlowGraph(data.final.final_flow, graph, data.final.blocked_edges || []);
      placeholder.appendChild(flowGraphContainer);
    }
  }

  // Fonction pour charger un graphe depuis une chaîne de texte
  function parseGraphInput() {
    try {
      const inputText = document.getElementById('graph-input').value;

      // Transformation du texte en un objet JavaScript
      // On enlève 'graph = ' s'il existe et on nettoie la chaîne
      const cleanedText = inputText.replace(/^graph\s*=\s*/, '').trim();

      // Évaluation sécurisée en remplaçant les tuples Python par des arrays JavaScript
      const processedText = cleanedText
        .replace(/\(/g, '[')
        .replace(/\)/g, ']');

      // Évaluation du texte pour obtenir l'objet
      const graphObj = Function('"use strict"; return ' + processedText)();

      // Conversion des tuples en arrays si nécessaire
      const processedGraph = {};
      for (const [key, value] of Object.entries(graphObj)) {
        processedGraph[key] = value.map(item =>
          Array.isArray(item) ? item : [item[0], item[1]]
        );
      }

      // Mise à jour du graphe
      graph = processedGraph;

      // Recréer le réseau avec les nouvelles données
      recreateNetwork();

      // Mise à jour de l'affichage
      updateGraphOutput();
    } catch (error) {
      alert('Erreur lors de l\'analyse du graphe : ' + error.message);
      console.error('Erreur d\'analyse :', error);
    }
  }

  // Fonction pour recréer le réseau avec les données du graphe
  function recreateNetwork() {
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
  }

  // Initialisation de l'interface
  initNetwork();

  // Gestion des modales
  document.querySelectorAll('.close-modal').forEach(button => {
    button.addEventListener('click', function() {
      this.closest('.modal').style.display = 'none';
    });
  });

  // Bouton pour analyser l'entrée de graphe
  document.getElementById('parse-btn').addEventListener('click', parseGraphInput);

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
      document.getElementById('results-section').style.display = 'none';
    }
  });

  // Bouton pour calculer le flot maximum via le service RO
  document.getElementById('send-btn').addEventListener('click', function() {
    if (Object.keys(graph).length === 0) {
      alert('Veuillez d\'abord créer ou charger un graphe');
      return;
    }

    // Conversion du graphe au format attendu par le service
    const serviceGraph = convertGraphToServiceFormat();
    
    // URL du service RO-Service
    const url = `${RO_SERVICE_URL}/api/calculate`;

    // Configuration de la requête
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ graph: serviceGraph })
    };

    // Afficher un message de chargement
    const sendBtn = document.getElementById('send-btn');
    const originalText = sendBtn.textContent;
    sendBtn.textContent = 'Calcul en cours...';
    sendBtn.disabled = true;

    // Envoi de la requête
    fetch(url, requestOptions)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Réponse du service RO:', data);
        displayResults(data);
        alert('Calcul terminé avec succès!');
      })
      .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors du calcul: ' + error.message);
      })
      .finally(() => {
        // Restaurer le bouton
        sendBtn.textContent = originalText;
        sendBtn.disabled = false;
      });
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
      recreateNetwork();
      updateGraphOutput();

      // Mettre à jour la zone de texte
      document.getElementById('graph-input').value = `graph = {
  "alfa": [("A", 45), ("B", 25), ("C", 30)],
  "A": [("D", 10), ("E", 15), ("G", 20)],
  "B": [("D", 20), ("E", 5), ("F", 15)],
  "C": [("F", 10), ("G", 15)],
  "D": [("omega", 30)],
  "E": [("omega", 10)],
  "F": [("omega", 20)],
  "G": [("omega", 40)]
}`;

      // Masquer les résultats précédents
      document.getElementById('results-section').style.display = 'none';
    }
  });
}); 