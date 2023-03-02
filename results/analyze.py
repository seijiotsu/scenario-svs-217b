import sys

def average_delay_for_node(node_of_interest,log_file):
    publications = {}
    latencies = []
    max_time = 0
    with open(log_file, 'r') as f:
        for line in f:
            line = [x.strip() for x in line.split(',')]

            time = float(line[0])
            node = line[1]
            mtype = line[2]
            mid = line[3]

            if mtype == 'PUB':
                publications[mid] = time
            if node != node_of_interest:
                continue
            if mtype == 'RECV':
                latencies.append(time - publications[mid])

            max_time = max(max_time, time)
        print(f"Average delay for node 0-0: {sum(latencies)/len(latencies)}")

if __name__ == "__main__":
    log_file = sys.argv[1]
    node_name = sys.argv[2]
    print("Processing", log_file)
    average_delay_for_node(node_name, log_file)

