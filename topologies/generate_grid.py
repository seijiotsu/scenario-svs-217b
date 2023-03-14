"""
Generates an N-N grid in the format of MiniNDN (See https://play.ndn.today/)
"""

N = 5
NODE_PREFIX = 'D'

with open(f'/home/developer/scenario-svs-217b/topologies/src/{N}x{N}_grid', 'w') as hdl:

    hdl.write('[nodes]\n')
    for i in range(N):
        for j in range(N):
            name = f'{NODE_PREFIX}{i*10 + j}'
            hdl.write(f'{name}: _ network=/world router=/{name}.Router/\n')
    
    hdl.write('[switches]\n')

    hdl.write('[links]\n')
    connections = set()
    for i in range(N):
        for j in range(N):
            # Connect (i, j) to its neighbors
            neighbors = [
                (i+1, j),
                (i-1, j),
                (i, j+1),
                (i, j-1)
            ]

            for i2, j2 in neighbors:
                if i2 >= 0 and i2 < N and j2 >=0 and j2 < N:
                    connections.add(tuple(sorted([(i, j), (i2, j2)])))
    
    for first, second in connections:
        # Calculate the names of the nodes from their coordinates
        first = first[0]*10 + first[1]
        second = second[0]*10 + second[1]

        hdl.write(f'{NODE_PREFIX}{first}:{NODE_PREFIX}{second} delay=10ms\n')