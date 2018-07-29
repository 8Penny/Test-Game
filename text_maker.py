import networkx as nx
g = nx.Graph()
g.add_edge('a', 'b')
g.add_edge('b', 'a')
g.add_edge('a', 'c')
print(nx.dijkstra_path(g, 'b', 'c'))