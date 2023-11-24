import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pylab as plt
import os
import glob

from analysis import LogData, read_log_file

def plot_line(points, label, marker, plotter=None):
    lists = sorted(points)
    if not points:
        print(f'Warning: label "{label}" was empty! Is this correct?')
        return
    x, y = zip(*lists)
    if plotter:
        plotter.plot(x, y, label=label, marker=marker)
    else:
        plt.plot(x, y, label=label, marker=marker)

cache = {}
def get_log_data(filepath, ignore_cache=False, timespan=None) -> LogData:
    """
    Use this as a wrapper to cache LogData reads, to speed up the program.
    """
    if ignore_cache or filepath not in cache:
        cache[filepath] = read_log_file(filepath, timespan)
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
    xticks = []
    show_every_nth_tick = 1

    for log in glob.glob(experiment_dir + f'randrec-*'):
        n_random, n_recent = [int(x) for x in log.split('/')[-1].split('-')[2:4]]
        ratio = n_recent
        xticks.append((ratio, f'{n_random}:{n_recent}'))
        log_data = get_log_data(log)
        if not log_data.complete():
            continue
        points.append((n_recent, log_data.latency_percentile_averages()[1]))
    plot_line(points, label='', marker='o')

    xticks.sort()
    xticks_points, xticks_labels = zip(*xticks)

    plt.xticks(xticks_points[::show_every_nth_tick], xticks_labels[::show_every_nth_tick])
    plt.xlabel(f'Random:Recent ratio for {topology_label}')
    plt.ylabel('Latency (ms)')
    fig.set_size_inches(6, 2.5)
    plt.grid()
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_rand_to_recent.png',bbox_inches='tight', pad_inches=0)
    plt.show()
    plt.clf()

def plot_latency_vs_sim_length(experiment_dir, topology_label):
    """
    Just some really quick sanity checking to make sure that the stop time doesn't affect latency nonlinearly
    """
    strategies = ['base', 'fullfrag', 'randrec', 'rand']
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, strategy in enumerate(strategies):
        points = []
        for log in glob.glob(experiment_dir + f'{strategy}-*'):
            log_data = get_log_data(log)
            # only works if drop rate 0.5, sry this is a quick hack. replace w/ your drop rate if this changes
            sim_length = int(log.split('-0.5')[0].split('-')[-1])
            if not log_data.complete():
                continue
            points.append((sim_length, log_data.latency_percentile_averages()[2]))
        plot_line(points, label=f'{topology_label}, {strategy}', marker=markers[i])


    plt.xlabel("Simulation length (seconds)")
    plt.ylabel(f"Latency (ms)")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01,1), loc='upper left')
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()

def plot_latency_vs_sim_length_single_file(
    dir,
    filename,
    label,
    num_points
):
    """
    Just some really quick sanity checking to make sure that the stop time doesn't affect latency nonlinearly
    """
    max_sim_length = get_log_data(dir + filename, True).end_time

    fig = matplotlib.pyplot.gcf()
    points = []
    for i in range(num_points):
        sim_length = (i/(num_points-1)) * max_sim_length + 10000
        print(sim_length)
        log_data = get_log_data(dir + filename, True, (0, sim_length))
        points.append((sim_length, log_data.latency_percentile_averages()[2]))
    plot_line(points, label=f'{label}', marker='o')

    plt.xlabel("Simulation length (seconds)")
    plt.ylabel(f"Latency (ms)")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(bbox_to_anchor=(1.01,1), loc='upper left')
    experiment_name = os.path.basename(os.path.normpath(dir))
    plt.savefig(f'{dir}/{experiment_name}.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()

def plot_connectivity_vs_latency(experiment_dir, topology_label, drop_rates, title, ylim=None, no_legend=True, ax = None):
    markers = ['o', '^', 'v', 's', '*']
    for i, drop_rate in enumerate(drop_rates):
        points = []
        logs = glob.glob(experiment_dir + f'*-{drop_rate}')
        for log in logs:
            if 'large_' in log:
                # hack
                average_degree = 2 * int(str(log).split('large_')[2].split('-')[0]) / 45
            elif '10x10' in log:
                num_edges = str(log).split('10x10_')[2].split('-')[0]
                num_edges = 180 if num_edges == 'grid' else int(num_edges)
                average_degree = 2 * num_edges / 100
            log_data = get_log_data(log)
            points.append((average_degree, log_data._90th_percentile_latency()))
        plot_line(points, label=f'Drop rate={drop_rate}', marker=markers[i], plotter=ax)
    ax.grid()
    if not no_legend:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=3)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(ylim)
    # experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    # ax.savefig(f'{experiment_dir}/{experiment_name}.png',bbox_inches='tight')
    # plt.show()
    # plt.clf()
    return ax

def plot_hop_count_vs_latency(experiment_dir, topology_label, drop_rates, title, ylim=None, no_legend=True, ax = None):
    markers = ['o', '^', 'v', 's', '*']
    for i, drop_rate in enumerate(drop_rates):
        points = []
        logs = glob.glob(experiment_dir + f'*-{drop_rate}')
        for log in logs:
            if 'large_' in log:
                # hack
                counts = {
                    44: 6.31,
                    50: 4.81,
                    55: 4.40,
                    63: 3.48,
                    71: 3.15
                }
                log_data = get_log_data(log)
                avg_hop_count = counts[int(str(log).split('large_')[2].split('-')[0])]
            points.append((avg_hop_count, log_data._90th_percentile_latency()))
        plot_line(points, label=f'Drop rate={drop_rate}', marker=markers[i], plotter=ax)
    ax.grid()
    if not no_legend:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=3)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(ylim)
    # experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    # ax.savefig(f'{experiment_dir}/{experiment_name}.png',bbox_inches='tight')
    # plt.show()
    # plt.clf()
    return ax

VARY_SUPP_TIMER_VALS = [50, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1200, 1400, 1600]
def plot_suppression_timer_vs_packet_count():
    fig = matplotlib.pyplot.gcf()
    points = []
    for supp_timer in VARY_SUPP_TIMER_VALS:
        log_data = get_log_data(f'/home/developer/scenario-svs-217b/analysis/logs/suppression_tuning_{supp_timer}ms/base-geant_large_55-44000-500-0.25')
        points.append((supp_timer, log_data.sync_pack))
    plot_line(points, label='Packet count vs. suppression timer (ms)', marker='o')
    plt.xlabel("Suppression timer (ms)")
    plt.ylabel(f"Total packets sent")
    plt.ylim(0, 8000)
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(loc='upper left')
    plt.savefig(f'/home/developer/scenario-svs-217b/analysis/logs/packet_count_vs_supp_timer.pdf',bbox_inches='tight', pad_inches=0)
    plt.show()
    plt.clf()

def plot_suppression_timer_vs_latency():
    fig = matplotlib.pyplot.gcf()
    points = []
    for supp_timer in VARY_SUPP_TIMER_VALS:
        log_data = get_log_data(f'/home/developer/scenario-svs-217b/analysis/logs/suppression_tuning_{supp_timer}ms/base-geant_large_55-44000-500-0.25')
        points.append((supp_timer, log_data._90th_percentile_latency()))
    plot_line(points, label='Latency vs. suppression timer (ms)', marker='o')
    plt.xlabel("Suppression timer (ms)")
    plt.ylabel(f"90th percentile latency (ms)")
    plt.ylim(0, 2000)
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(loc='upper left')
    plt.savefig(f'/home/developer/scenario-svs-217b/analysis/logs/latency_vs_supp_timer.pdf',bbox_inches='tight', pad_inches=0)
    plt.show()
    plt.clf()

def plot_latency_vs_packets():
    fig = matplotlib.pyplot.gcf()
    points = []
    for supp_timer in VARY_SUPP_TIMER_VALS:
        log_data = get_log_data(f'/home/developer/scenario-svs-217b/analysis/logs/suppression_tuning_{supp_timer}ms/base-geant_large_55-44000-500-0.25')
        points.append((log_data.sync_pack, log_data._90th_percentile_latency()))
    x, y = zip(*sorted(points))
    plt.scatter(x, y)
    plt.xlabel(f"Total packets sent")
    plt.ylabel("90th percentile latency (ms)")
    # plt.ylim(0, 2000)
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.savefig(f'/home/developer/scenario-svs-217b/analysis/logs/latency_vs_packets.pdf',bbox_inches='tight', pad_inches=0)
    plt.show()
    plt.clf()

def plot_connectivity_vs_packets(experiment_dir, topology_label, drop_rates, title, ylim=None, packet_type='all', as_proportion=True, no_legend=True, ax=None):
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's', '*']
    for i, drop_rate in enumerate(drop_rates):
        points = []
        logs = glob.glob(experiment_dir + f'*-{drop_rate}')
        for log in logs:
            if 'large_' in log:
                # hack
                average_degree = 2 * int(str(log).split('large_')[2].split('-')[0]) / 45
            elif '10x10' in log:
                num_edges = str(log).split('10x10_')[2].split('-')[0]
                num_edges = 180 if num_edges == 'grid' else int(num_edges)
                average_degree = 2 * num_edges / 100
            log_data = get_log_data(log)
            if packet_type == 'all':
                num_packets = log_data.sync_pack
            elif packet_type == 'publish':
                num_packets = log_data.num_publish_interests
            elif packet_type == 'suppression':
                num_packets = log_data.num_suppression_interests
            elif packet_type == 'periodic':
                num_packets = log_data.num_periodic_interests
            else:
                raise Exception(f'Unknown packet type "{packet_type}"')
            if packet_type != 'all' and as_proportion:
                points.append((average_degree, num_packets / log_data.sync_pack))
            else:
                points.append((average_degree, num_packets))
        plot_line(points, label=f'drop rate={drop_rate}', marker=markers[i], plotter=ax)
    ax.grid()
    if not no_legend:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=3)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(ylim)
    elif as_proportion:
        ax.set_ylim([0, 1])
    # experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    # plt.savefig(f'{experiment_dir}/{experiment_name}_{packet_type}_packets_{("percent" if as_proportion else "count")}.png',bbox_inches='tight')#, pad_inches=0)
    # plt.show()
    # plt.clf()

def plot_drop_rate_vs_latency(experiment_dir, topology_label):
    fig = matplotlib.pyplot.gcf()
    drop_rates = [0] + [i/20 for i in range(1, 21)]
    points = []
    for i, drop_rate in enumerate(drop_rates):
        logs = glob.glob(experiment_dir + f'base-geant_small_*-{drop_rate}')
        if not logs:
            continue
        log = logs[0]
        log_data = get_log_data(log)
        points.append((drop_rate, log_data.latency_percentile_averages()[2]))
    plot_line(points, label=f'{topology_label} (minimum spanning tree)', marker='*')
    plt.xlabel("Drop rate")
    plt.ylabel(f"Latency (ms)")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend(loc='upper left')
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}.png',bbox_inches='tight', pad_inches=0)
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

def plot_exp_latency_decrease(timer, drop_rates, title, ylim=None, no_legend=True, ax = None):
    markers = ['o', 'v', '*']
    for i, drop_rate in enumerate(drop_rates):
        points = []
        logs = glob.glob(f'/home/developer/scenario-svs-217b/analysis/logs/geant_large_week_8_{timer}/' + f'*-{drop_rate}')
        logs_upgraded = glob.glob(f'/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_{timer}/' + f'*-{drop_rate}')
        for j in range(len(logs)):
            average_degree = 2 * int(str(logs[j]).split('large_')[2].split('-')[0]) / 45
            log_data = get_log_data(logs[j])
            log_data_upgraded = get_log_data(logs_upgraded[j])
            points.append((average_degree, log_data_upgraded._90th_percentile_latency() / log_data._90th_percentile_latency()))
        plot_line(points, label=f'Drop rate={drop_rate}', marker=markers[i], plotter=ax)
    ax.grid()
    if not no_legend:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=3)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(ylim)
    return ax

def plot_exp_count_decrease(timer, drop_rates, title, ylim=None, no_legend=True, ax = None):
    markers = ['o', 'v', '*']
    for i, drop_rate in enumerate(drop_rates):
        points = []
        logs = glob.glob(f'/home/developer/scenario-svs-217b/analysis/logs/geant_large_week_8_{timer}/' + f'*-{drop_rate}')
        logs_upgraded = glob.glob(f'/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_{timer}/' + f'*-{drop_rate}')
        for j in range(len(logs)):
            average_degree = 2 * int(str(logs[j]).split('large_')[2].split('-')[0]) / 45
            log_data = get_log_data(logs[j])
            log_data_upgraded = get_log_data(logs_upgraded[j])
            points.append((average_degree, log_data_upgraded.sync_pack / log_data.sync_pack))
        plot_line(points, label=f'Drop rate={drop_rate}', marker=markers[i], plotter=ax)
    ax.grid()
    if not no_legend:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=3)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(ylim)
    return ax

if __name__ == '__main__':
    # fig, axs = plt.subplots(nrows=3, ncols=1)
    # plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.155)
    # plt.xlabel("Average hop count")
    # plt.ylabel(f"90th percentile latency (ms)")
    # # plt.suptitle('GÉANT Latency vs. Connectivity', fontweight='bold')
    # fig.set_size_inches(6, 6.5)

    # ylim = [0, 10000]
    # plot_hop_count_vs_latency(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_250/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='Periodic timer of 0.25 sec',
    #     ylim=ylim,
    #     ax=axs[0]
    # )
    # plot_hop_count_vs_latency(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_1000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='Periodic timer of 1 sec',
    #     ylim=ylim,
    #     ax=axs[1]
    # )
    # plot_hop_count_vs_latency(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_4000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='Periodic timer of 4 sec',
    #     ylim=ylim,
    #     no_legend=False,
    #     ax=axs[2]
    # )

    # plt.savefig('/home/developer/scenario-svs-217b/analysis/logs/hop_count_vs_latency.pdf')
    # plt.clf()

    # fig, axs = plt.subplots(nrows=3, ncols=1)
    # plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.155)
    # plt.xlabel("Average node degree")
    # plt.ylabel(f"90th percentile latency (ms)")
    # # plt.suptitle('GÉANT Latency vs. Connectivity', fontweight='bold')
    # fig.set_size_inches(6, 6.5)

    # ylim = [0, 10000]
    # plot_connectivity_vs_latency(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_250/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='Periodic timer of 0.25 sec',
    #     ylim=ylim,
    #     ax=axs[0]
    # )
    # plot_connectivity_vs_latency(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_1000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='Periodic timer of 1 sec',
    #     ylim=ylim,
    #     ax=axs[1]
    # )
    # plot_connectivity_vs_latency(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_4000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='Periodic timer of 4 sec',
    #     ylim=ylim,
    #     no_legend=False,
    #     ax=axs[2]
    # )

    # plt.savefig('/home/developer/scenario-svs-217b/analysis/logs/connectivity_vs_latency_exp.pdf')
    # plt.clf()

    # fig, axs = plt.subplots(nrows=3, ncols=1)
    # plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.155)
    # plt.xlabel("Average node degree")
    # plt.ylabel(f"Total sync interest count")
    # # plt.suptitle('GÉANT total sync interest counts', fontweight='bold')
    # fig.set_size_inches(6, 6.5)

    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_250/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 0.25 sec)',
    #     ylim=[0, 60000],
    #     ax=axs[0]
    # )
    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_1000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 1 sec)',
    #     ylim=[0, 15000],
    #     ax=axs[1]
    # )
    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_4000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 4 sec)',
    #     ylim=[0, 6000],
    #     ax=axs[2],
    #     no_legend=False
    # )

    # plt.savefig('/home/developer/scenario-svs-217b/analysis/logs/total_packet_count_exp.pdf')
    # plt.clf()

    # fig, axs = plt.subplots(nrows=3, ncols=1)
    # plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.155)
    # plt.xlabel("Average node degree")
    # plt.ylabel(f"Periodic sync interests fraction")
    # # plt.suptitle('GÉANT periodic sync interests fraction', fontweight='bold')
    # fig.set_size_inches(6, 6.5)

    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_250/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 0.25 sec)',
    #     ylim=[0, 1],
    #     packet_type='periodic',
    #     ax=axs[0]
    # )
    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_1000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 1 sec)',
    #     ylim=[0, 1],
    #     packet_type='periodic',
    #     ax=axs[1]
    # )
    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_4000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 4 sec)',
    #     ylim=[0, 1],
    #     packet_type='periodic',
    #     ax=axs[2],
    #     no_legend=False
    # )

    # plt.savefig('/home/developer/scenario-svs-217b/analysis/logs/periodic_fraction_exp.pdf')
    # plt.clf()

    # fig, axs = plt.subplots(nrows=3, ncols=1)
    # plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.155)
    # plt.xlabel("Average node degree")
    # plt.ylabel(f"Suppression sync interests fraction")
    # # plt.suptitle('GÉANT periodic sync interests fraction', fontweight='bold')
    # fig.set_size_inches(6, 6.5)

    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_250/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 0.25 sec)',
    #     ylim=[0, 1],
    #     packet_type='suppression',
    #     ax=axs[0]
    # )
    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_1000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 1 sec)',
    #     ylim=[0, 1],
    #     packet_type='suppression',
    #     ax=axs[1]
    # )
    # plot_connectivity_vs_packets(
    #     experiment_dir='/home/developer/scenario-svs-217b/analysis/logs/upgraded_geant_large_week_8_4000/',
    #     topology_label='GÉANT',
    #     drop_rates=[0, 0.125, 0.25, 0.375, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 4 sec)',
    #     ylim=[0, 1],
    #     packet_type='suppression',
    #     ax=axs[2],
    #     no_legend=False
    # )

    # plt.savefig('/home/developer/scenario-svs-217b/analysis/logs/suppression_exp.pdf')
    # plt.clf()

    # """
    # This guy is just a one-off
    # """
    # fig, axs = plt.subplots(nrows=3, ncols=1)
    # plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.155)
    # plt.xlabel("Average node degree")
    # plt.ylabel(f"% 90th percentile latency (after/before) exp(suppression)")
    # fig.set_size_inches(6, 6.5)

    # plot_exp_latency_decrease(
    #     timer='250',
    #     drop_rates=[0, 0.25, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 0.25 sec)',
    #     ylim=[0.8, 1.2],
    #     ax=axs[0]
    # )
    # plot_exp_latency_decrease(
    #     timer='1000',
    #     drop_rates=[0, 0.25, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 1 sec)',
    #     ylim=[0.8, 1.2],
    #     ax=axs[1]
    # )
    # plot_exp_latency_decrease(
    #     timer='4000',
    #     drop_rates=[0, 0.25, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 4 sec)',
    #     ylim=[0.8, 1.2],
    #     ax=axs[2],
    #     no_legend=False
    # )

    # plt.savefig('/home/developer/scenario-svs-217b/analysis/logs/exp_sup_latency_change.pdf')
    # plt.clf()

    # fig, axs = plt.subplots(nrows=3, ncols=1)
    # plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.155)
    # plt.xlabel("Average node degree")
    # plt.ylabel(f"% total packet count (after/before) exp(suppression)")
    # fig.set_size_inches(6, 6.5)

    # plot_exp_count_decrease(
    #     timer='250',
    #     drop_rates=[0, 0.25, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 0.25 sec)',
    #     ylim=[0.5, 1.2],
    #     ax=axs[0]
    # )
    # plot_exp_count_decrease(
    #     timer='1000',
    #     drop_rates=[0, 0.25, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 1 sec)',
    #     ylim=[0.5, 1.2],
    #     ax=axs[1]
    # )
    # plot_exp_count_decrease(
    #     timer='4000',
    #     drop_rates=[0, 0.25, 0.5],
    #     title='GÉANT (Publish rate of 1/sec, Periodic timer of 4 sec)',
    #     ylim=[0.5, 1.2],
    #     ax=axs[2],
    #     no_legend=False
    # )

    # plt.savefig('/home/developer/scenario-svs-217b/analysis/logs/exp_sup_count_change.pdf')
    # plt.clf()

    plot_suppression_timer_vs_packet_count()
    plot_suppression_timer_vs_latency()
    plot_latency_vs_packets()