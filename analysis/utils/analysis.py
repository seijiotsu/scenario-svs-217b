from collections import defaultdict
from os import times
import sys
import numpy
import math
from typing import Tuple


class LogData:
    def __init__(self, nodes, messages, publish_times, receive_times, latencies,
                 end_time, sync_pack, sync_bytes, mtu_size, num_publish_interests,
                 num_suppression_interests, num_periodic_interests):
        self.nodes = nodes
        self.messages = messages
        self.publish_times = publish_times
        self.receive_times = receive_times
        self.latencies = latencies
        self.end_time = end_time
        self.sync_pack = sync_pack
        self.sync_bytes = sync_bytes
        self.mtu_size = mtu_size
        self.num_publish_interests = num_publish_interests
        self.num_suppression_interests = num_suppression_interests
        self.num_periodic_interests = num_periodic_interests
        self._90th_percentile_latency_value = None

    def _get_message_latency_percentiles(self, message: Tuple[str, int]) -> Tuple[float, float]:
        """
        Returns the 50th and 90th percentile latencies for a given message
        """
        return (
            numpy.percentile(self.latencies[message], 50),
            numpy.percentile(self.latencies[message], 90)
        )

    def latency_percentile_averages(self) -> Tuple[float, float, float]:
        """
        Returns the average of each latency percentile (50th, 90th and 100th)
        """
        # This code is copied from somewhere else so I'm not 100% sure what some
        # of it means (like the scale thing)
        # I'm assuming this is  to normalize values s.t they have a standard
        # deviation of 1; the original author did this
        scale = math.sqrt(1)
        nums50 = []
        nums90 = []
        nums100 = []
        for message in self.latencies:
            nums50.append(numpy.percentile(self.latencies[message], 50))
            nums90.append(numpy.percentile(self.latencies[message], 90))
            nums100.append(max(self.latencies[message]))
        
        return (
            numpy.average(nums50) / scale,
            numpy.average(nums90) / scale,
            numpy.average(nums100) / scale
        )

    def _90th_percentile_latency(self) -> float:
        """
        Get all the latencies, put them in one big boat, find the 90th percentile.
        """
        if self._90th_percentile_latency_value == None:
            latencies = [latency for _, message_latency in self.latencies.items() for latency in message_latency]
            self._90th_percentile_latency_value = numpy.percentile(latencies, 90)
        return self._90th_percentile_latency_value

    def total_pubs_per_second(self) -> float:
        return len(self.latencies) / (self.end_time / 1000)

    def complete(self) -> bool:
        """
        Whether or not the log data is finished and includes sync pack, sync byte,
        mtu size, etc.
        """
        # If MTU_SIZE=0, that means we didn't parse to the end of the file. MTU
        # size will never be zero normally, because then nothing would ever
        # transmit and there would be no point to that...
        return self.mtu_size != 0

def read_log_file(filepath, timespan=None) -> LogData:
    print(filepath)
    """
    Read the log file and collect some very basic data about it for further
    analysis.
    """
    # The timespan we want to analyze in the log file. By default it is the
    # entire log file.
    if timespan:
        min_time, max_time = timespan
    else:
        min_time, max_time = 0, float('inf')

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
    # Keep track of some other statistics
    end_time = 0
    sync_byte = 0
    sync_pack = 0
    mtu_size = 0
    num_publish_interests = 0
    num_suppression_interests = 0
    num_periodic_interests = 0
    with open(filepath, 'r') as hdl:
        for line in hdl:
            # Edge case: end of the file, printing stats and stuff.
            if line.startswith('SYNC'):
                val = int(line.split('=')[1])
                if line.startswith('SYNC_PACK'):
                    sync_pack = val
                if line.startswith('SYNC_BYTE'):
                    sync_byte = val
                continue
            if line.startswith('MTU_SIZE'):
                mtu_size = min(int(line.split('=')[1]), len(nodes))
                continue

            line = line.split(',')
            timestamp = float(line[0])
            node = line[1][1:]
            action = line[2]

            if not (min_time <= timestamp <= max_time):
                break

            # line is an INTEREST message
            if action == 'INTEREST':
                interestType = line[3].strip()
                if interestType == 'PUBLISH':
                    num_publish_interests += 1
                    # There's a very specific edge case we have to handle here.
                    # Basically, the NDN simulator creates new data in its 'PUB'
                    # messages, and then sends out that data one millisecond
                    # later in a 'INTEREST,PUBLISH' message. This is usually
                    # not a big deal, so we approximate the time that the data
                    # was sent out by the timestamp of the 'PUB' message.
                    # HOWEVER, for the initial sync interest, i.e. the one that
                    # sends out the first piece of data, we set a random timer
                    # to wait in order to space them all out, thus the actual
                    # time that other nodes will know about the new piece of data
                    # may be many seconds after it was actually 'created'. So
                    # we need to use the INTEREST,PUBLISH timestamp rather than
                    # the 'PUB' timestamp for the first and only the first
                    # sequence number.
                    if len(publish_times[node]) == 1:
                        # This INTEREST,PUBLISH message is the actual time that
                        # the first node sent out its initial sequence number.
                        publish_times[node][1] = timestamp
                elif interestType == 'SUPPRESSION':
                    num_suppression_interests += 1
                elif interestType == 'PERIODIC':
                    num_periodic_interests += 1
                else:
                    raise Exception(f'Unknown interest type "{interestType}"')
            else:
                # Normal case: line is either a PUB or a RECV message.
                data = line[3]
                end_time = max(timestamp, end_time)
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

    return LogData(nodes, messages, publish_times, receive_times, latencies,
                   end_time, sync_pack, sync_byte, mtu_size,
                   num_publish_interests, num_suppression_interests, 
                   num_periodic_interests)


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

    nodes, messages, publish_times, receive_times, latencies = read_log_file(
        filepath)

    # print(sorted(list(nodes)))
    # print(sorted(list(messages)))
    # print(avg_pub_recv_delay_between_nodes('A1', 'A4', publish_times, receive_times))
    # print(numpy.percentile(latencies[('A22', 13)], 50))
    # print(numpy.percentile(latencies[('A33', 13)], 50))

    # Calculate the average latency per message
    # print(numpy.average([numpy.average(x) for x in latencies.values()]))
