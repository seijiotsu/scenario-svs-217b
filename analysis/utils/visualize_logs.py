import matplotlib
import matplotlib.pylab as plt
import os
import math
import glob
import numpy

def get_key(fp, index_of_metric=2):
    filename = os.path.splitext(os.path.basename(fp))[0]
    #sort glob files based on rate speed i.e index [2]
    partofInterest = filename.split('-')[index_of_metric]
    intpart = partofInterest.split('_')[0]
    return int(intpart)
def add_plot(result_dictionary, label, marker):
    lists = sorted(result_dictionary.items())
    x, y = zip(*lists)
    plt.plot(x, y, label=label, marker=marker)
def read_log_for_overhead_and_latency(filename):
    #feel free to move this function elsewhere
    publications = {}
    latencies = {}
    max_time = 0
    sync_pack = 0
    sync_byte = 0
    
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('SYNC_'):
                val = int(line.split('=')[1])
                if line.startswith('SYNC_PACK'):
                    sync_pack = val
                if line.startswith('SYNC_BYTE'):
                    sync_byte = val
                    
                continue
            
            line = [x.strip() for x in line.split(',')]
            
            time = float(line[0])
            node = line[1]
            mtype = line[2]
            mid = line[3]
            
            if mtype == 'PUB':
                publications[mid] = time
            
            if mtype == 'RECV':
                if mid not in latencies:
                    latencies[mid] = []
                latencies[mid].append(time - publications[mid])
                
            max_time = max(max_time, time)
    
    return latencies, max_time, sync_pack, sync_byte
def merge_dict(dict1,dict2):
    d = dict1.copy()
    d.update(dict2)
    return d
def set_p(latency_dictionary, max_time, sync_pack, sync_byte):

    results50 = {}
    results90 = {}
    results_pack = {}
    results_byte = {}
    scale = math.sqrt(1) #original author does this
    # I'm assuming this is  to normalize values s.t they have a standard deviation of 1
    nums50 = []
    nums90 = []
    for messageID in latency_dictionary:
        # print(f'messageID (key for latency dic) is {messageID}')
        nums50.append(numpy.percentile(latency_dictionary[messageID], 50))
        nums90.append(numpy.percentile(latency_dictionary[messageID], 90))

    # print(f'Max time: {max_time}')
    total_pubs_per_sec = len(latency_dictionary)/(max_time/1000)
    # print(f'k is {total_pubs_per_sec}')
    results50[total_pubs_per_sec] = numpy.average(nums50) / scale
    results90[total_pubs_per_sec] = numpy.average(nums90) / scale
    results_pack[total_pubs_per_sec] = sync_pack
    results_byte[total_pubs_per_sec] = sync_byte


    return results50, results90, results_pack, results_byte

def plot_overhead_across_runs(experiment_dir, methods, topology):
    #, topology, randrec_tuples, methods, publish_rates, losses
    
    fig = matplotlib.pyplot.gcf()
    markers = ['o', '^', 'v', 's']
    for i, method in enumerate(methods):
        results = {}
        logs =  glob.glob(experiment_dir + f'{method}-*')
        #sort log by pub speed (i.e index 2)
        logs = sorted(logs, key=get_key)
        for log in logs:
            processed_log = read_log_for_overhead_and_latency(log)
            results50, results90, packets, bytes = set_p(*processed_log)
            results = merge_dict(results, bytes)
        add_plot(results, label=f'{topology},{method}', marker=markers[i])


    plt.xlabel("Total publications per second")
    plt.ylabel("Overhead")
    fig.set_size_inches(6, 2.5)
    plt.grid()
    plt.legend()
    experiment_name = os.path.basename(os.path.normpath(experiment_dir))
    plt.savefig(f'{experiment_dir}/{experiment_name}.pdf',bbox_inches='tight', pad_inches=0)  
    plt.show() 
    
    

if __name__ == '__main__':
    dir = "C:/Users/joshc/Desktop/CS217B/scenario-svs-217b/analysis/logs/6x6_grid_plot1/"
    methods = ['base', 'fullfrag', 'randrec', 'rand']
    topology = '6x6'
    plot_overhead_across_runs(dir, methods, topology)