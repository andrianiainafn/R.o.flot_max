# Constructeur de Graphe - Service RO

## Description

Cette application web permet de construire et visualiser des graphes, puis de calculer le flot maximum en utilisant le service RO-Service.

## Fichiers créés

- `main.html` : Interface utilisateur pour la construction de graphes
- `main.js` : Logique JavaScript pour l'interaction avec le service RO-Service
- `start_service.py` : Script pour démarrer facilement le service RO-Service

## Fonctionnalités

### Interface utilisateur
- **Construction visuelle de graphes** : Ajout/suppression de nœuds et arêtes via l'interface
- **Entrée directe** : Saisie de graphes au format Python
- **Visualisation interactive** : Affichage du graphe avec la bibliothèque vis.js
- **Export** : Sauvegarde du graphe au format Python

### Calcul de flot maximum
- **Intégration avec RO-Service** : Communication avec le service backend
- **Affichage des résultats** : Flot maximum, étapes du calcul, chemins d'augmentation
- **Format de données** : Conversion automatique du format graphe vers le format attendu par le service

## Utilisation

### 1. Démarrer le service RO-Service

```bash
python start_service.py
```

Le service sera accessible sur `http://localhost:4321`

### 2. Ouvrir l'interface

Ouvrez le fichier `main.html` dans votre navigateur web.

### 3. Construire un graphe

Vous pouvez construire un graphe de deux façons :

#### Option A : Interface visuelle
1. Cliquez sur l'espace de travail pour ajouter des nœuds
2. Faites glisser entre les nœuds pour créer des arêtes
3. Entrez les poids des arêtes dans la modal

#### Option B : Entrée directe
1. Utilisez la zone de texte pour saisir un graphe au format Python
2. Cliquez sur "Analyser et générer le graphe"

### 4. Calculer le flot maximum

1. Assurez-vous que votre graphe contient des nœuds source (ex: "alfa") et puits (ex: "omega")
2. Cliquez sur "Calculer le flot maximum"
3. Les résultats s'afficheront dans la section "Résultats du calcul de flot maximum"

## Format du graphe

Le graphe doit être au format Python avec des nœuds source et puits :

```python
graph = {
    "alfa": [("A", 45), ("B", 25), ("C", 30)],  # nœud source
    "A": [("D", 10), ("E", 15), ("G", 20)],
    "B": [("D", 20), ("E", 5), ("F", 15)],
    "C": [("F", 10), ("G", 15)],
    "D": [("omega", 30)],
    "E": [("omega", 10)],
    "F": [("omega", 20)],
    "G": [("omega", 40)]
    # "omega" est le nœud puits
}
```

## Différences avec index.html/index.js

- **Service backend** : Utilise RO-Service au lieu d'app.py
- **URL de service** : `http://localhost:4321` au lieu de `http://localhost:5000`
- **Endpoint** : `/calculate` au lieu de `/flow-max`
- **Format de données** : Conversion automatique vers le format attendu par RO-Service
- **Affichage des résultats** : Section dédiée pour afficher les résultats détaillés du calcul

## Dépendances

- **Frontend** : vis.js (inclus via CDN)
- **Backend** : RO-Service (Flask)
- **Navigateur** : Support moderne des navigateurs web

## Résolution de problèmes

### Service non accessible
- Vérifiez que le service RO-Service est démarré sur le port 4321
- Consultez les logs du service pour identifier les erreurs

### Erreurs CORS
- Le service RO-Service doit être configuré pour accepter les requêtes depuis le frontend
- Vérifiez la configuration CORS dans le service

### Format de données incorrect
- Assurez-vous que le graphe contient des nœuds source et puits
- Vérifiez que les capacités sont des nombres positifs 