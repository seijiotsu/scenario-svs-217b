#!/bin/sh



./waf configure
./waf
mkdir -p ./exp_log_files_josh/



./build/topology_6_node_bottleneck 4_Row 4_Col 1000_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 20_S_STOP 0_DROP_RATE 4_MTU > ./exp_log_files_josh/FULL_Method-4_Row-4_Col-1000_MS_INTER_SLOW-100_MS_INTER_FAST-0_Nodes_Pub_Fast-0_RECENT_PUB-99999_RANDOM_PUB-10_S_STOP-0_DROP_RATE-4_MTU.log &
