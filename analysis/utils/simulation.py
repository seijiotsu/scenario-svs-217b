from asyncio.subprocess import DEVNULL
import subprocess
import sys
import os
import time
from multiprocessing import Process

from .colors import Colors

ROOT_PATH = '/home/developer/scenario-svs-217b'
PROCESSED_TOPOLOGIES_PATH = ROOT_PATH + '/topologies/processed/'
SIMULATOR_PATH = ROOT_PATH + '/build/simulate'
LOGGING_PATH = ROOT_PATH + '/analysis/logs/'

def randrecent(topology_name, n_random, n_recent, publish_rate_ms,
               stop_second, drop_rate, subfolder) -> str:
    """
    Run a Random-Recent, Random or Recent simulation. Returns the output file.
    """
    output_file = LOGGING_PATH + subfolder + '/' + \
        f'randrec-{topology_name}-{n_random}-{n_recent}-{publish_rate_ms}-{stop_second}-{drop_rate}'
    print(Colors.HEADER + f'Running {output_file}...' + Colors.ENDC, end='')
    sys.stdout.flush()
    if os.path.isfile(output_file):
        print('already exists!')
    else:
        start_time = time.time()
        with open(output_file, 'w') as hdl:
            # args = [
            #     SIMULATOR_PATH, PROCESSED_TOPOLOGIES_PATH + topology_name,
            #     str(n_random), str(n_recent), str(publish_rate_ms),
            #     str(stop_second), str(drop_rate), '0'
            # ]
            # print(' '.join(args))
            subprocess.run(args, stdout=hdl, stderr=DEVNULL)
        end_time = time.time()
        print(f'done in {(end_time - start_time):.2f} sec')
    return output_file

def rand(topology_name, n_random, n_recent, publish_rate_ms,
               stop_second, drop_rate, subfolder) -> str:
    """
    Run a Random-Recent, Random or Recent simulation. Returns the output file.
    """

    output_file = LOGGING_PATH + subfolder + '/' + \
        f'rand-{topology_name}-{n_random}-{n_recent}-{publish_rate_ms}-{stop_second}-{drop_rate}'
    print(Colors.HEADER + f'Running {output_file}...' + Colors.ENDC, end='')
    sys.stdout.flush()
    if os.path.isfile(output_file):
        print('already exists!')
    else:
        start_time = time.time()
        with open(output_file, 'w') as hdl:
            subprocess.run([SIMULATOR_PATH, PROCESSED_TOPOLOGIES_PATH + topology_name,
                            str(n_random), str(n_recent), str(publish_rate_ms),
                            str(stop_second), str(drop_rate), '0'], stdout=hdl, stderr=DEVNULL)
        end_time = time.time()
        print(f'done in {(end_time - start_time):.2f} sec')
    return output_file

def base(topology_name, publish_rate_ms, stop_second, drop_rate, subfolder) -> str:
    """
    Run a base simulation (send the entire state vector in a single interest)
    """
    output_file = LOGGING_PATH + subfolder + '/' + \
        f'base-{topology_name}-{publish_rate_ms}-{stop_second}-{drop_rate}'
    sys.stdout.flush()
    if os.path.isfile(output_file):
        print(Colors.HEADER + f'{output_file}' + Colors.ENDC + ' already exists!')
    else:
        start_time = time.time()
        print(Colors.OKGREEN + f'Running {output_file}' + Colors.ENDC)
        with open(output_file, 'w') as hdl:
            args = [SIMULATOR_PATH, PROCESSED_TOPOLOGIES_PATH + topology_name,
                '99999', '0', str(publish_rate_ms), str(stop_second), str(drop_rate), '0']
            # print(' '.join(args))
            subprocess.run(args, stdout=hdl, stderr=DEVNULL)
        end_time = time.time()
        print(f'{output_file} DONE in {(end_time - start_time):.2f} sec')
    return output_file


def fragment(topology_name, publish_rate_ms, stop_second, drop_rate, mtu_size, subfolder) -> str:
    """
    Run a full fragment simulation (send out the entire state vector in multiple
    sync interests, with `mtu_size` states per interest).
    """
    output_file = LOGGING_PATH + subfolder + '/' + \
        f'fullfrag-{topology_name}-{publish_rate_ms}-{stop_second}-{drop_rate}-{mtu_size}'
    print(Colors.HEADER + f'Running {output_file}...' + Colors.ENDC, end='')
    sys.stdout.flush()
    if os.path.isfile(output_file):
        print('already exists!')
    else:
        start_time = time.time()
        with open(output_file, 'w') as hdl:
            subprocess.run([SIMULATOR_PATH, PROCESSED_TOPOLOGIES_PATH + topology_name,
                            '99999', '0', str(publish_rate_ms), str(stop_second), str(drop_rate), str(mtu_size)],
                        stdout=hdl, stderr=DEVNULL)
        end_time = time.time()
        print(f'done in {(end_time - start_time):.2f} sec')
    return output_file


def conduct_full_simulation(topologies,
                            publish_rates,
                            stop_seconds,
                            drop_rates,
                            randrec_tuples,
                            mtu_sizes,
                            subfolder=''):
    """
    Runs base, full frag, and randrec simulations for each topology, pub rate,
    stop second, and drop rate.
    """
    if not os.path.exists(LOGGING_PATH + subfolder):
        os.mkdir(LOGGING_PATH + subfolder)
    for topology in topologies:
        for publish_rate in publish_rates:
            for stop_second in stop_seconds:
                for drop_rate in drop_rates:
                    # Simulate base first
                    process = Process(target=base, args=(topology, publish_rate, stop_second, drop_rate, subfolder))
                    process.start()
                    # base(topology, publish_rate, stop_second, drop_rate, subfolder)
                    # # Simulate fullfrag next
                    # for mtu_size in mtu_sizes:
                    #     fragment(topology, publish_rate, stop_second, drop_rate,
                    #              mtu_size, subfolder)
                    #     #simulate random, where n_random is mtu_size
                    #     rand(topology, mtu_size, 0, publish_rate, stop_second,
                    #         drop_rate, subfolder)
                    # # Simulate randrec last
                    # for n_random, n_recent in randrec_tuples:
                    #     randrecent(topology, n_random, n_recent, publish_rate,
                    #                stop_second, drop_rate, subfolder)


if __name__ == '__main__':
    randrecent(
        sys.argv[1],
        n_random=sys.argv[2],
        n_recent=sys.argv[3],
        publish_rate_ms=sys.argv[4],
        stop_second=sys.argv[5],
        drop_rate=sys.argv[6]
    )