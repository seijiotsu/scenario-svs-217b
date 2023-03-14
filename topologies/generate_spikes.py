"""
Generates N spikes around a central node in the format of MiniNDN (See https://play.ndn.today/)
"""

N = 16
NODE_PREFIX = 'A'

with open(f'/home/developer/scenario-svs-217b/topologies/src/{N}_spike', 'w') as hdl:

    hdl.write('[nodes]\n')
    hdl.write(f'{NODE_PREFIX}: _ network=/world router=/{NODE_PREFIX}.Router/\n')
    for i in range(N):
            name = f'{NODE_PREFIX}{i}'
            hdl.write(f'{name}: _ network=/world router=/{name}.Router/\n')
    
    hdl.write('[switches]\n')

    hdl.write('[links]\n')
    connections = set()
    for i in range(N):
        hdl.write(f'{NODE_PREFIX}:{NODE_PREFIX}{i} delay=10ms\n')