import networkx as nx
# Create a Graph object
G = nx.Graph()

# Add the nodes to the graph, with properties
G.add_node("Max", age=20, gender="male")
G.add_node("Alice", age=22, gender="female")
G.add_node("Bob", age=21, gender="male")

# Add the edges to the graph
G.add_edge("Max", "Alice", label="knows")
G.add_edge("Alice", "Max", label="knows")
G.add_edge("Alice", "Bob", label="knows")
print(G)