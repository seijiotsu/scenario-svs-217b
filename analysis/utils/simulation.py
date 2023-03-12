from asyncio.subprocess import DEVNULL
import subprocess
import sys

from .colors import Colors

ROOT_PATH = '/home/developer/scenario-svs-217b'
PROCESSED_TOPOLOGIES_PATH = ROOT_PATH + '/topologies/processed/'
RANDRECENT_PATH = ROOT_PATH + '/build/randrecent'


def randrecent(topology_name, n_random, n_recent, publish_rate_ms,
               stop_second, drop_rate) -> str:
    """
    Run a Random-Recent, Random or Recent simulation. Returns the output file.
    """
    output_file = ROOT_PATH + '/analysis/logs/' + f'{topology_name}-{n_random}-{n_recent}-{publish_rate_ms}-{stop_second}-{drop_rate}'
    print(Colors.HEADER + f'Running {output_file}...' + Colors.ENDC, end='')
    sys.stdout.flush()
    with open(output_file, 'w') as hdl:
        subprocess.run([RANDRECENT_PATH, PROCESSED_TOPOLOGIES_PATH + topology_name,
                        str(n_random), str(n_recent), str(publish_rate_ms),
                        str(stop_second), str(drop_rate)], stdout=hdl, stderr=DEVNULL)
    print('done')
    return output_file
def base_full():
    return output_file
if __name__ == '__main__':
    randrecent(
        sys.argv[1],
        n_random=sys.argv[2],
        n_recent=sys.argv[3],
        publish_rate_ms=sys.argv[4],
        stop_second=sys.argv[5],
        drop_rate=sys.argv[6]
    )