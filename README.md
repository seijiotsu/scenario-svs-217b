## Overview

For 217B and for my capstone I built a fair amount of Python code to easily run experiments. Most of my time was spent in the `analysis` directory, where the most important file, `run.sh` lives. This script automatically compiles everything, builds all topologies, and then runs any simulations that haven't been run yet. It runs experiments that are specified inside of json files, for example `config_seiji.json`.

## JSON config files

These config files are JSON objects with child key: value pairs that specify the names of an experiment (for readability) and the parameters of an experiment.

- `enable` specifies whether an experiment will be run when the file is loaded.

- `metadata` is just some comments to help remember what an experiment does.

- `topologies` is an array of topologies that the experiment will be run against.

- `publish_rates` Time between an individual node publishing data

- `stop_seconds` Simulation time the simulation will execute for

- `drop_rates` Drop rate the simulation will use

- `randrec_tuples` Old code from my 217B project. Leave this empty unless you are playing around with random-recent Sync interests.

- `mtu_sizes` Old code from my 217B project. Leave this empty unless you are playing around with fragmented Sync interests.

- `subfolder` Folder in `analysis/logs` that the simulation results will go into.

Note that the simulation will run all combinations of these parameters. So if you have for example publish rates [10, 100] and stop seconds [5, 15] then it will run simulations on publish_rate=10 and stop_second=5, then publih_rate=10 and stop_second=15, etc. and put these all into the output folder for further analysis.

## utils/visualize_logs.py

This is the other important Python file that I used a lot. What this file does is it has a lot of code to plot different types of graphs. Sorry it is a bit messy. It relies on the other files in the utils folder to pre-process logs, and smartly loads logs at most once and caches them in memory if they are referenced multiple times.

## Notes on my Capstone simulations

I apologise for the poor naming of my experiments, it was done over a long period of time and going back and renaming everything may have broken something.

### Logs + JSON configs
Figures 1, 2 and 3 in my capstone were generated using the data in `analysis/logs/geant_large_week_8_*`. It is named that way because I ran those simulations during Spring Quarter 2023 Week 8.

Figures 5, 6, and 8 in my capstone were generated using the data in `analysis/logs/upgraded_geant_large_week_8_*` for the exponential suppression timer, and `analysis/logs/upgraded3_geant_large_week_8_*` for exponential suppression timer and RTT optimization.

Figure 7 was generated with all of the `analysis/logs/suppression_tuning_*` folders.

The `analysis/logs/upgraded_test_{before,after}` folders were from when I was testing whether or not I correctly implemented RTT optimization.

It shouldn't be too difficult to find the corresponding JSON configs for these files.

### extensions/ndn-svs/main.cpp

I had to make changes to `main.cpp` for each of my different experiments. Since periodic timer duration is specified in this file, I manually changed it before running the corresponding simulation specified in my JSON files. For instance, for the `upgraded_geant_large_week_8_250` simulations I had to change the periodic timer duration to 250 in `main.cpp` then recompile and run `run.sh`. This is not the most elegant way to do it, I know. Maybe one day it can be integrated into the JSON config directly but that would require a lot of changes I wasn't sure how to make.

Also the code for exponential suppression timer and exponential suppression timer + RTT optimization is implemented in this file.

### topologies

The `src/` subdirectory contains Mini-NDN topologies which can be imported into the online NDN play viewer directly, and when you run `run.sh` these process into something that the NDN simulator used to run the simulations can read.