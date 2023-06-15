
#!/bin/bash
cd /home/developer/scenario-svs-217b
#if running for the first time, comment out if you need to
./waf configure
#compile all scenario .cpp's
./waf

#build topologies
python3 ./topologies/build.py
#clean up topologies
python3 ./topologies/clean_topologies.py

cd /home/developer/scenario-svs-217b/analysis
python3 main.py /home/developer/scenario-svs-217b/analysis/config_capstone_prelim.json