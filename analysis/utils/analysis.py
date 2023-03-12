from collections import defaultdict
import sys
import numpy

def read_log_file(filepath):
    """
    Read the log file and collect some very basic data about it for further
    analysis.
    """
    nodes = set()
    messages = set()
    # Keep track of publish times for messages, e.g. /A1::1. So we need a nested
    # dictionary.
    publish_times = defaultdict(dict)
    # Keep track of the receive times per node. For example, keep track of when
    # node A1 recieved A2::1, A23::4, etc. So index by sender and then by
    # message, leading to a doubly-nested dictionary.
    receive_times = defaultdict(lambda: defaultdict(dict))
    # Keep track of the latencies for a given message
    latencies = defaultdict(list)
    with open(filepath, 'r') as hdl:
        for line in hdl:
            # Edge case: end of the file, printing stats and stuff.
            if line.startswith('SYNC'):
                continue

            # Normal case: line is either a PUB or a RECV message.
            timestamp, node, action, data = line.split(',')
            timestamp = float(timestamp)
            node = node[1:]
            data_node, seq_number = data.split('::')
            data_node = data_node[1:]
            seq_number = int(seq_number)


            # Add this node and the message to our list of nodes and messages
            nodes.add(node)
            messages.add((node, seq_number))

            if action == 'PUB':
                publish_times[node][seq_number] = timestamp
            elif action == 'RECV':
                receive_times[node][data_node][seq_number] = timestamp
                latency = timestamp - publish_times[data_node][seq_number]
                latencies[(data_node, seq_number)].append(latency)
            else:
                raise Exception('Unrecognized message!')

    return nodes, messages, publish_times, receive_times, latencies

def avg_pub_recv_delay_between_nodes(node1, node2, publish_times, receive_times):
    """
    Uses the data in publish_time and receive_time to calculate the average time
    it takes for messages published by node1 to be received by node2 and vice
    versa.

    NOTE: We ignore any seq numbers that the receiver did not receive, because
    in larger graphs it may be in the middle of propagating by the time that
    our simulation ends.
    """
    delays = []
    for seq_no, publish_time in publish_times[node1].items():
        if seq_no in receive_times[node1][node2]:
            delays.append(receive_times[node1][node2][seq_no] - publish_time)
    for seq_no, publish_time in publish_times[node2].items():
        if seq_no in receive_times[node2][node1]:
            delays.append(receive_times[node2][node1][seq_no] - publish_time)

    return sum(delays) / len(delays)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Hardcoded to test
        filepath = '/home/developer/scenario-svs-217b/exp_log_files_seiji/med_clusters.txt'
    
    nodes, messages, publish_times, receive_times, latencies = read_log_file(filepath)

    # print(sorted(list(nodes)))
    # print(sorted(list(messages)))
    # print(avg_pub_recv_delay_between_nodes('A1', 'A4', publish_times, receive_times))
    # print(numpy.percentile(latencies[('A22', 13)], 50))
    # print(numpy.percentile(latencies[('A33', 13)], 50))

    # Calculate the average latency per message
    print(numpy.average([numpy.average(x) for x in latencies.values()]))