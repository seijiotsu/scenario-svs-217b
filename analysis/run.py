import numpy

import utils.analysis
import utils.simulation


def simulate_and_analyze_randrecent(topology_name, n_random, n_recent, publish_rate_ms,
                                    stop_second, drop_rate) -> str:
    out = utils.simulation.randrecent(topology_name, n_random, n_recent,
                                      publish_rate_ms, stop_second, drop_rate)
    nodes, messages, publish_times, receive_times, latencies = utils.analysis.read_log_file(
        out)

    average_latency = numpy.average(
        [numpy.average(x) for x in latencies.values()])

    # _90th_percentile_latency = numpy.percentile([item for sublist in latencies for item in sublist], 90)

    print(f'A total of {len(messages)} message(s) were sent by {len(nodes)} node(s). Each node sent on average {len(messages)/len(nodes):.2f} message(s)')
    print(f'average latency per message: {average_latency:.2f} ms')
    # print(f'90th percentile latency: {_90th_percentile_latency:.2f} ms')
    # print(avg_pub_recv_delay_between_nodes('A1', 'A4', publish_times, receive_times))
    # print(numpy.percentile(latencies[('A22', 13)], 50))
    # print(numpy.percentile(latencies[('A33', 13)], 50))
    print()

def sim_and_analyze_base():
    print()
simulate_and_analyze_randrecent('med_clusters', 8, 8, 300, 3, 0.3)
simulate_and_analyze_randrecent('med_clusters', 4, 4, 300, 3, 0.3)
simulate_and_analyze_randrecent('med_clusters', 2, 2, 300, 3, 0.3)
simulate_and_analyze_randrecent('med_clusters', 1, 1, 300, 3, 0.3)

sim_and_analyze_base('', )