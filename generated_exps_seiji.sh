python3 ./topologies/build.py
python3 ./topologies/clean_topologies.py

./waf

./build/comsci217b 4_Row 4_Col 300_MS_INTER_SLOW 100_MS_INTER_FAST 0_Nodes_Pub_Fast 0_RECENT_PUB 99999_RANDOM_PUB 5_S_STOP 0_DROP_RATE /home/developer/scenario-svs-217b/topologies/processed/med_clusters 4_MTU  > ./exp_log_files_seiji/med_clusters.txt &