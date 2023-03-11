#!/bin/sh
python3 ./topologies/build.py
python3 ./topologies/clean_topologies.py

./waf
mkdir -p ./exp_log_files_josh/

./build/comsci217b 4_Row 4_Col 1000_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 20_S_STOP 0_DROP_RATE /home/developer/scenario-svs-217b/topologies/processed/butterfly 4_MTU > ./exp_log_files_josh/FULL_Method-butterfly-1000_MS_INTER_SLOW-100_MS_INTER_FAST-0_Nodes_Pub_Fast-0_RECENT_PUB-99999_RANDOM_PUB-10_S_STOP-0_DROP_RATE-4_MTU.log &
#./build/comsci217b 4_Row 4_Col 1000_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 20_S_STOP 0_DROP_RATE /home/developer/scenario-svs-217b/topologies/processed/topo-6-zeroPos 4_MTU > ./exp_log_files_josh/FULL_Method-6node_zeroPos-1000_MS_INTER_SLOW-100_MS_INTER_FAST-0_Nodes_Pub_Fast-0_RECENT_PUB-99999_RANDOM_PUB-10_S_STOP-0_DROP_RATE-4_MTU.log &

# ./build/comsci217b 4_Row 4_Col 850_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 20_S_STOP 0_DROP_RATE /home/developer/scenario-svs-217b/topologies/processed/topo-6 4_MTU > ./exp_log_files_josh/FULL_Method-6node-850_MS_INTER_SLOW-100_MS_INTER_FAST-0_Nodes_Pub_Fast-0_RECENT_PUB-99999_RANDOM_PUB-10_S_STOP-0_DROP_RATE-4_MTU.log &
# ./build/comsci217b 4_Row 4_Col 1150_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 20_S_STOP 0_DROP_RATE /home/developer/scenario-svs-217b/topologies/processed/topo-6 4_MTU > ./exp_log_files_josh/FULL_Method-6node-1150_MS_INTER_SLOW-100_MS_INTER_FAST-0_Nodes_Pub_Fast-0_RECENT_PUB-99999_RANDOM_PUB-10_S_STOP-0_DROP_RATE-4_MTU.log &

# ./build/comsci217b 4_Row 4_Col 700_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 20_S_STOP 0_DROP_RATE /home/developer/scenario-svs-217b/topologies/processed/topo-6 4_MTU > ./exp_log_files_josh/FULL_Method-6node-700_MS_INTER_SLOW-100_MS_INTER_FAST-0_Nodes_Pub_Fast-0_RECENT_PUB-99999_RANDOM_PUB-10_S_STOP-0_DROP_RATE-4_MTU.log &
# ./build/comsci217b 4_Row 4_Col 1300_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 20_S_STOP 0_DROP_RATE /home/developer/scenario-svs-217b/topologies/processed/topo-6 4_MTU > ./exp_log_files_josh/FULL_Method-6node-1300_MS_INTER_SLOW-100_MS_INTER_FAST-0_Nodes_Pub_Fast-0_RECENT_PUB-99999_RANDOM_PUB-10_S_STOP-0_DROP_RATE-4_MTU.log &

