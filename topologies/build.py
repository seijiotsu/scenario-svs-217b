import os

for file in os.scandir('/home/developer/scenario-svs-217b/topologies/src'):
    print(f'Building topology "{file.name}"...', end='')
    with open(file.path, 'r') as hdl:
        # assumes [switches] is empty
        nodes, links = hdl.read().split('[switches]')

    # remove headers    
    nodes = [node for node in nodes.split('\n')[1:] if node]
    links = links.split('\n')[2:]

    # grab just the node names
    nodes = [node.split(':')[0] for node in nodes]

    # format links into (source, dest, bandwidth, metric, delay, queue)
    # ngl idk what metric means so we will just set it as 1
    # and queue is the "max packets for transmission queue on the link (both
    # directions)"
    # Links are originally formatted as e.g. 'new_1:new_4 delay=10ms'
    links = [link.replace(' delay=', ':').split(':') for link in links]
    links = [link for link in links if link[0]]
    links = [
        (link[0], link[1], '10Mbps', 1, link[2], 20)
        for link in links
    ]

    # Write to file
    with open(f'/home/developer/scenario-svs-217b/topologies/processed/{file.name}', 'w') as hdl:
        hdl.write('router\n')
        hdl.write('# node\tcomment\tyPos\txPos\n')
        for node in nodes:
            hdl.write(f'{node}\tNA\t0\t0\n')
        hdl.write('\nlink\n')
        hdl.write('# src\tdest\tbandwidth\tmetric\tdelay\tqueue\n')
        for link in links:
            hdl.write(f'{link[0]}\t{link[1]}\t{link[2]}\t{link[3]} {link[4]}\t{link[5]}\n')

    print('done')