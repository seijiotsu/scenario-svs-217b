import numpy
import json
import utils.analysis
import utils.simulation


def simulate_and_analyze_randrecent(topology_name, n_random, n_recent, publish_rate_ms,
                                    stop_second, drop_rate) -> str:
    out = utils.simulation.randrecent(topology_name, n_random, n_recent,
                                      publish_rate_ms, stop_second, drop_rate)
    nodes, messages, publish_times, receive_times, latencies = utils.analysis.read_log_file(out)

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

def collapsible_main():
    #
    # This simulation is designed to reproduce appendix A, B and C of the paper by
    # Xiao et al.
    #
    utils.simulation.conduct_full_simulation(
        topologies=['6x6_grid'],
        publish_rates=[100,125,150,175,200,225,250,275,300,500,1000],
        stop_seconds=[3],
        drop_rates=[0.25],
        randrec_tuples=[(9, 9)],
        mtu_sizes=[18],
        subfolder='6x6_grid_plot1'
    )

    #
    # This simulation is designed to reproduce appendix A, B and C of the paper by
    # Xiao et al. on two small clusters connected by a single bridge
    #
    utils.simulation.conduct_full_simulation(
        topologies=['small_clusters'],
        publish_rates=[150,175,200,225,250,275,300,500,1000],
        stop_seconds=[3],
        drop_rates=[0.25],
        randrec_tuples=[(8, 8)],
        mtu_sizes=[16],
        subfolder='small_clusters_plot1'
    )

    #
    # This simulation is designed to reproduce appendix A, B and C of the paper by
    # Xiao et al. on two medium clusters connected by a single bridge
    #
    utils.simulation.conduct_full_simulation(
        topologies=['med_clusters'],
        publish_rates=[175,225,275,500,750,1000],
        stop_seconds=[3],
        drop_rates=[0.25],
        randrec_tuples=[(18, 18)],
        mtu_sizes=[36],
        subfolder='med_clusters_plot1'
    )

    #
    # This simulation is designed to test MTU vs latency
    #
    utils.simulation.conduct_full_simulation(
        topologies=['8x8_grid'],
        publish_rates=[500],
        stop_seconds=[3],
        drop_rates=[0.5],
        randrec_tuples=[(16, 16), (8, 8), (4, 4), (2, 2), (1, 1)],
        mtu_sizes=[32, 16, 8, 4, 2],
        subfolder='latency_vs_mtu_1'
    )
def read_config(jsonfile):
    print(jsonfile)
    fp = open(jsonfile)
    experiment_config = json.load(fp)
    return experiment_config
def execute_config(experiment_config):
    for experiment_key in experiment_config.keys():
        experiment = experiment_config[experiment_key]
        if experiment["enable"] == 'false':
            print(f'Experiment {experiment_key} skipped')
            continue
        topologies = experiment["topologies"]
        publish_rates= experiment["publish_rates"]
        stop_seconds= experiment["stop_seconds"]
        drop_rates= experiment["drop_rates"]
        randrec_lists = experiment["randrec_tuples"]
        randrec_tuples = []
        for each_randrec_list in randrec_lists:
            randrec_tuples.append(tuple(each_randrec_list))
        mtu_sizes=experiment["mtu_sizes"]
        subfolder=experiment["subfolder"]

        utils.simulation.conduct_full_simulation(topologies, 
                                                 publish_rates, 
                                                 stop_seconds, 
                                                 drop_rates, 
                                                 randrec_tuples,
                                                 mtu_sizes,
                                                 subfolder)
        

if __name__ == '__main__':
    experiment_config = read_config("/home/developer/scenario-svs-217b/analysis/config_josh.json")
    execute_config(experiment_config)