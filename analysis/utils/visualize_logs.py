import matplotlib
import matplotlib.pylab as plt
import os
import glob

from analysis import LogData, read_log_file

def plot_line(points, label, marker):
    lists = sorted(points)
    if not points:
        print(f'Warning: label "{label}" was empty! Is this correct?')
        return
    x, y = zip(*lists)
    plt.plot(x, y, label=label, marker=marker)

cache = {}
def get_log_data(filepath) -> LogData:
    """
    Use this as a wrapper to cache LogData reads, to speed up the program.
    """
    if filepath not in cache:
        cache[filepath] = read_log_file(filepath)
    return cache[filepath]

def plot_versus_publications(experiment_dir, strategies, topology_label, graph_type):
    """
    Plot a `graph_type` against the total number of publications per second.

    args:
    -   experiment_dir: the directory where all of the logs we want to use are
                        stored in.
    -   methods:    the strategies that we want to plot (e.g. base, randrecent)
    -   topology_label: human-readable label for the topology in the final graph
    -   graph_type: packet overhead, byte overhead, or latency overhead
    """
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, strategy in enumerate(strategies):
        points = []
        for log in glob.glob(experiment_dir + f'{strategy}-*'):
            log_data = get_log_data(log)
            if not log_data.complete():
                continue
            if graph_type == 'bytes':
                points.append((log_data.total_pubs_per_second(), log_data.sync_bytes))
            elif graph_type == 'packets':
                points.append((log_data.total_pubs_per_second(), log_data.sync_pack))
            elif graph_type == 'latency':
                points.append((log_data.total_pubs_per_second(), log_data.latency_percentile_averages()[1]))
        plot_line(points, label=f'{topology_label}, {strategy}', marker=markers[i])


    plt.xlabel("Total publications per second")
    if graph_type == 'latency':
        plt.ylabel(f"Latency (ms)")
    else:
        plt.ylabel(f"Overhead ({graph_type})")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend()
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_{graph_type}.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()

def plot_versus_latency(experiment_dir, strategies, topology_label, graph_type):
    """
    args:
    -   experiment_dir: the directory where all of the logs we want to use are
                        stored in.
    -   methods:    the strategies that we want to plot (e.g. base, randrecent)
    -   topology_label: human-readable label for the topology in the final graph
    -   graph_type: packet overhead, or byte overhead
    """
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, strategy in enumerate(strategies):
        points = []
        for log in glob.glob(experiment_dir + f'{strategy}-*'):
            log_data = get_log_data(log)
            if not log_data.complete():
                continue
            if graph_type == 'bytes':
                points.append((log_data.latency_percentile_averages()[1], log_data.sync_bytes))
            if graph_type == 'packets':
                points.append((log_data.latency_percentile_averages()[1], log_data.sync_pack))
        plot_line(points, label=f'{topology_label}, {strategy}', marker=markers[i])


    plt.xlabel("Latency (ms)")
    plt.ylabel(f"Overhead ({graph_type})")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend()
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_latency_vs_{graph_type}.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()

def plot_latency_vs_mtu(experiment_dir, topology_label):
    """
    Holding stop second, publish rate, drop rate constant.
    """
    strategies = ['base', 'fullfrag', 'randrec', 'rand']
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, strategy in enumerate(strategies):
        points = []
        for log in glob.glob(experiment_dir + f'{strategy}-*'):
            log_data = get_log_data(log)
            if not log_data.complete():
                continue
            points.append((log_data.mtu_size / len(log_data.nodes) * 100, log_data.latency_percentile_averages()[1]))
        plot_line(points, label=f'{topology_label}, {strategy}', marker=markers[i])


    plt.xlabel("MTU size (as a % of total nodes)")
    plt.ylabel(f"Latency (ms)")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01,1), loc='upper left')
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_mtu_vs_latency.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()

def plot_byte_overhead_vs_mtu(experiment_dir, topology_label):
    """
    Holding stop second, publish rate, drop rate constant.
    """
    strategies = ['base', 'fullfrag', 'randrec', 'rand']
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, strategy in enumerate(strategies):
        points = []
        for log in glob.glob(experiment_dir + f'{strategy}-*'):
            log_data = get_log_data(log)
            if not log_data.complete():
                continue
            points.append((log_data.mtu_size / len(log_data.nodes) * 100, log_data.sync_bytes))
        plot_line(points, label=f'{topology_label}, {strategy}', marker=markers[i])


    plt.xlabel("MTU size (as a % of total nodes)")
    plt.ylabel(f"Overhead (bytes)")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01,1), loc='upper left')
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_mtu_vs_bytes.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()


def plot_packet_overhead_vs_mtu(experiment_dir, topology_label):
    """
    Holding stop second, publish rate, drop rate constant.
    """
    strategies = ['base', 'fullfrag', 'randrec', 'rand']
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, strategy in enumerate(strategies):
        points = []
        for log in glob.glob(experiment_dir + f'{strategy}-*'):
            log_data = get_log_data(log)
            if not log_data.complete():
                continue
            points.append((log_data.mtu_size / len(log_data.nodes) * 100, log_data.sync_pack))
        plot_line(points, label=f'{topology_label}, {strategy}', marker=markers[i])


    plt.xlabel("MTU size (as a % of total nodes)")
    plt.ylabel(f"Overhead (packets)")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01,1), loc='upper left')
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_mtu_vs_packets.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()

def plot_random_recent_tradeoff(experiment_dir, topology_label):
    """
    Hold a bunch of stuff constant, plot the tradeoff between random and recent.
    """
    fig = matplotlib.pyplot.gcf()
    points = []
    xticks_points = []
    xticks_labels = []
    show_every_nth_tick = 2

    for log in glob.glob(experiment_dir + f'randrec-*'):
        n_random, n_recent = [int(x) for x in log.split('/')[-1].split('-')[2:4]]
        ratio = n_recent / n_random
        xticks_points.append(ratio)
        xticks_labels.append(f'{n_random}:{n_recent}')
        log_data = get_log_data(log)
        if not log_data.complete():
            continue
        points.append((n_recent / n_random, log_data.latency_percentile_averages()[1]))
        plot_line(points, label='', marker='o')
    plt.xticks(xticks_points[::show_every_nth_tick], xticks_labels[::show_every_nth_tick])
    plt.xlabel('Random:Recent ratio')
    plt.ylabel('Latency (ms)')
    fig.set_size_inches(6, 2.5)
    plt.grid()
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_rand_to_recent.png',bbox_inches='tight', pad_inches=0)
    plt.show()
    plt.clf()

def run_full_xiao_plots(experiment_dir, topology_label):
    """
    Generate all plots in the style of Appendix A, B and C from Xiao et al., and
    also generate new plots vs. latency

    Note: Xiao plots keep latency, MTU and rand-rec distribution constant.
    If you don't do this then these functions won't work.
    """
    strategies = ['base', 'fullfrag', 'randrec', 'rand']
    plot_versus_publications(experiment_dir, strategies, topology_label, 'bytes')
    plot_versus_publications(experiment_dir, strategies, topology_label, 'packets')
    plot_versus_publications(experiment_dir, strategies, topology_label, 'latency')
    plot_versus_latency(experiment_dir, strategies, topology_label, 'bytes')
    plot_versus_latency(experiment_dir, strategies, topology_label, 'packets')


if __name__ == '__main__':
    # run_full_xiao_plots(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/6x6_grid_plot1/',
    #     topology_label='6x6'
    # )
    # run_full_xiao_plots(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/small_clusters_plot1/',
    #     topology_label='Small Clusters'
    # )
    # run_full_xiao_plots(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/med_clusters_plot1/',
    #     topology_label='Medium Clusters'
    # )
    # plot_latency_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/latency_vs_mtu_1/',
    #     topology_label='8x8'
    # )
    # plot_byte_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/latency_vs_mtu_1/',
    #     topology_label='8x8'
    # )
    # plot_latency_vs_mtu(
    #     experiment_dir = '/home/developer/scenario-svs-217b/analysis/logs/6x6_mtu_experiment/',
    #     topology_label = '6x6'
    # )
    # plot_byte_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/6x6_mtu_experiment/',
    #     topology_label='6x6'
    # )
    # plot_packet_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/6x6_mtu_experiment/',
    #     topology_label='6x6'
    # )
    # plot_latency_vs_mtu(
    #     experiment_dir = '/home/developer/scenario-svs-217b/analysis/logs/kite_4_5x5_250MS/',
    #     topology_label = '6x6'
    # )
    # plot_byte_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/kite_4_5x5_250MS/',
    #     topology_label='6x6'
    # )
    # plot_packet_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/kite_4_5x5_250MS/',
    #     topology_label='6x6'
    # )
    # plot_latency_vs_mtu(
    #     experiment_dir = '/home/developer/scenario-svs-217b/analysis/logs/connected_spikes_250MS/',
    #     topology_label = 'Connected Spikes'
    # )
    # plot_byte_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/connected_spikes_250MS/',
    #     topology_label='Connected Spikes'
    # )
    # plot_packet_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/connected_spikes_250MS/',
    #     topology_label='Connected Spikes'
    # )
    # plot_latency_vs_mtu(
    #     experiment_dir = '/home/developer/scenario-svs-217b/analysis/logs/sparse_250MS/',
    #     topology_label = 'Sparse'
    # )
    # plot_byte_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/sparse_250MS/',
    #     topology_label='Sparse'
    # )
    # plot_packet_overhead_vs_mtu(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/sparse_250MS/',
    #     topology_label='Sparse'
    # )
    plot_random_recent_tradeoff(
        experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/test_random_recent_variation/',
        topology_label='6x6'
    )
    plot_random_recent_tradeoff(
        experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/kite_randrec_variation/',
        topology_label='6x6'
    )
    plot_random_recent_tradeoff(
        experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/sparse_randrec_variation/',
        topology_label='6x6'
    )
    plot_random_recent_tradeoff(
        experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/spikes_randrec_variation/',
        topology_label='6x6'
    )