from collections import defaultdict, deque

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
            return False  # No augmenting path

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
        return True

    def print_flow(self):
        print("Current Flow:")
        for u in self.graph:
            for v, _ in self.graph[u]:
                print(f"{u} -> {v}: {self.flow[u][v]}/{self.residual[u][v] + self.flow[u][v]}")
        print()

    def ford_fulkerson(self, source, sink):
        print("Step 1: Marking Nodes and Improving Flow")
        while self.improve_flow(source, sink):
            pass

        print("Final Maximum Flow:")
        self.print_flow()
        max_flow = 0
        for v, _ in self.graph[source]:
            max_flow += self.flow[source][v]
        return max_flow

# Example graph
graph = {
    "alfa": [("A", 35), ("B", 25), ("C", 25)],
    "A": [("D", 10), ("E", 5), ("G", 20)],
    "B": [("D", 10), ("E", 5), ("F", 15)],
    "C": [("F", 10), ("G", 15)],
    "D": [("omega", 20)],
    "E": [("omega", 10)],
    "F": [("omega", 20)],
    "G": [("omega", 35)],
}

# Create the graph object
g = Graph(graph)

# Compute the maximum flow
source = "alfa"
sink = "omega"
max_flow = g.ford_fulkerson(source, sink)

print(f"\nThe maximum flow from {source} to {sink} is {max_flow}")
