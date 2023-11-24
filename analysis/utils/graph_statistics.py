import networkx as nx

def load_topology(topology_name):
    with open('/home/developer/scenario-svs-217b/topologies/src/' + topology_name, 'r') as hdl:
        text = hdl.read()

    nodes, links = text.split('[switches]\n[links]')
    nodes = [node.split(':')[0] for node in nodes.split('\n')[1:-1]]
    links = [link.split(':') for link in [link.split(' ')[0] for link in links.split('\n')[1:]]]

    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(links)

    return g

if __name__ == '__main__':
    topologies = [44, 50, 55, 63, 71]
    for topology in topologies:
        name = f'geant_large_{topology}'
        g = load_topology(name)
        print(f'Average hop count for {name}: {nx.average_shortest_path_length(g):.2f}')