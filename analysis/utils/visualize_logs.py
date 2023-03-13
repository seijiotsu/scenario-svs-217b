import matplotlib
import matplotlib.pylab as plt
import os
import glob

from analysis import LogData, read_log_file

def plot_line(points, label, marker):
    lists = sorted(points)
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

def plot_overhead_across_runs(experiment_dir, strategies, topology_label, overhead_type):
    """
    args:
    -   experiment_dir: the directory where all of the logs we want to use are
                        stored in.
    -   methods:    the strategies that we want to plot (e.g. base, randrecent)
    -   topology_label: human-readable label for the topology in the final graph
    """
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, method in enumerate(strategies):
        points = []
        for log in glob.glob(experiment_dir + f'{method}-*'):
            log_data = get_log_data(log)
            if overhead_type == 'bytes':
                points.append((log_data.total_pubs_per_second(), log_data.sync_bytes))
            elif overhead_type == 'packets':
                points.append((log_data.total_pubs_per_second(), log_data.sync_pack))
        plot_line(points, label=f'{topology_label}, {method}', marker=markers[i])


    plt.xlabel("Total publications per second")
    plt.ylabel(f"Overhead ({overhead_type})")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend()
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}_{overhead_type}.png',bbox_inches='tight', pad_inches=0)  
    plt.show()
    plt.clf()

if __name__ == '__main__':
    dir = "/home/developer/scenario-svs-217b/analysis/logs/6x6_grid_plot1/"
    strategies = ['base', 'fullfrag', 'randrec', 'rand']
    topology_label = '6x6'
    plot_overhead_across_runs(dir, strategies, topology_label, 'bytes')
    plot_overhead_across_runs(dir, strategies, topology_label, 'packets')