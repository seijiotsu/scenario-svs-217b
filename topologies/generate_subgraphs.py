""" 
Generate an N x N grid and a list of its subgraphs with increasingly more links
in the format of MiniNDN
"""


class Graph:  
    """ undirected graph """

    def __init__(self,name):
        self.name = name
        self.nodes = []
        self.adj = {} # map node to its neighbors 

    def add_node(self, v):
        self.nodes.append(v)
        self.adj[v] = set()

    def add_edge(self, u, v):
        if u not in self.nodes:
            self.add_node(u)
        if v not in self.nodes:
            self.add_node(v)
        self.adj[u].add(v)
        self.adj[v].add(u)

    def add_edges_from(self, edges):
        for u,v in edges:
            self.add_edge(u, v)
          
    def edges(self):
        edges = []
        for u,neighbors in self.adj.items():
            for v in neighbors:
                if u < v: # make sure each edge is only added once
                    edges.append((u,v))
        return edges

    def BFS(self, return_trace=False): 
        order = [] 
        edges = []
        visited = {node:False for node in self.nodes}

        root = self.nodes[0]
        queue = [root]
        visited[root] = True
        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in self.adj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
                    edges.append((u, v))

        if return_trace:
            return order, edges
        else:
            return order
        
    def __str__(self):
        str = f"Graph {self.name}: \n"
        for u,neighbors in self.adj.items():
            str += f"{u}: {neighbors}\n"
        return str
    
    def save_graph_for_MiniNDN(self, filepath):
        with open(f'{filepath}/{self.name}', 'w') as hdl:
            hdl.write('[nodes]\n')
            for node in self.nodes:
                hdl.write(f'{node}: _ network=/world router=/{node}.Router/\n')

            hdl.write('[switches]\n')
            hdl.write('[links]\n')
            for u,v in self.edges():
                hdl.write(f'{u}:{v} delay=10ms\n')




# generate an N by N grid as Graph object
def generate_grid(N, node_prefix):
    nodes = [[None for _ in range(N)] for _ in range(N)] # map indices to node names
    edges = [] # list of (u,v) pairs
    # add nodes
    for i in range(N):
        for j in range(N):
            # name = f'{node_prefix}x{i}y{j}'
            name = f'{node_prefix}{i}{j}'
            nodes[i][j] = name
    # add edges
    for i in range(N):
        for j in range(N):
            u = (i, j)
            # Connect (i, j) to its neighbors
            neighbors = [
                (i+1, j),
                (i-1, j),
                (i, j+1),
                (i, j-1)
            ]
            for i2,j2 in neighbors:
                if i2 >= 0 and i2 < N and j2 >= 0 and j2 < N:
                    v = (i2, j2)
                    if u < v: # make sure each edge is only added once
                        edge = (nodes[u[0]][u[1]], nodes[v[0]][v[1]])
                        edges.append(edge)

    G = Graph(f"{N}x{N}_grid")
    G.add_edges_from(edges)
    return G


# generate a list of subgraphs of G that add different ratios of edges 
# onto a minimum spanning tree of G
def generate_subgraphs(G, ratios):
    edges = G.edges()
    # get minimum spanning tree of G
    order, edges0 = G.BFS(return_trace=True)
    #G0 = Graph(f"{G.name}_0")
    #G0.add_edges_from(edges0)
    # get subgraphs
    subgraphs = []
    other_edges = list(set(edges) - set(edges0))
    for i,ratio in enumerate(ratios):
        num_edges = int(len(other_edges)*ratio)
        edges_i = other_edges[:num_edges]
        edges_i = edges0 + edges_i
        G_i = Graph(f"{G.name}_sub{i}")
        G_i.add_edges_from(edges_i)
        subgraphs.append(G_i)

    return subgraphs








if __name__ == "__main__":
    N = 6
    G = generate_grid(N, 'A')
    print("G: ", G)
    ratios = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    subgraphs = generate_subgraphs(G, ratios)
    filepath = "scenario-svs-217b/topologies/src/"
    for i,graph in enumerate(subgraphs):
        print(f"G{i}: ", graph)
        graph.save_graph_for_MiniNDN(filepath)


                    




    
