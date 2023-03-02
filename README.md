Prerequisites
=============

Install latest version of ndnSim and configure/build with waf.

```
./waf configure
./waf
```

## Implementation detail
The prefix of the current participant is ALWAYS included in the sync interest, no matter how other parameters are set.

## Examples
1. ``./build/large-grid 6row 6col 1000ms_inter_slow 100ms_inter_fast 4nodes_publish_fast 0RecentPublishedToInclude 30RandomToInclude 7s_stop 0.02_pkt_drop_rate``
2. ``./build/large-grid 6row 6col 1000ms_inter_slow 100ms_inter_fast 4nodes_publish_fast 0RecentPublishedToInclude 99999RandomToInclude 7s_stop 0.02_pkt_drop_rate``
   1. 99999 prefix to include essentially force to include the whole state vector
3. ``./build/large-grid 6row 6col 1000ms_inter_slow 100ms_inter_fast 4nodes_publish_fast 0RecentPublishedToInclude 30RandomToInclude 7s_stop 0.02_pkt_drop_rate 18_mtu``
   1. MTU=18 prefix. Do segmentation based on this.
   2. However, only select 30 prefixes in total. 

Note: fragmentation is orthogonal to how the subset of states are selected. Fragmentation only operate on the result of the prefix selection.


## Generate Experiments

Here we have a gen_exp.py file to generate a set of experiments. I used python3.8 when writing this file.
Inside the gen_exp.py, you can set up various parameters like drop_rate, topN, and etc. But methods need to be manually configured or hard-coded into this gen again. Let me know if you want to add new methods. Currently it supports three methods:

You can also set the parallel level by setting the PERGROUP parameter in the gen_exp.py.

1) Baseline (without frag)

2) Baseline (frag) //Send multiple sync-interest fragmented by MTU

3) Random  //Send ONE sync-interest based on mtu

4) Mix (rand + recent) //Send ONE sync-interest based on mtu, recent can be tuned inside gen_exp.py

Run the configured gen_exp.py and you will get a shell script. In which it will run waf and create a log folders, in which the log flies will be named by the parameters for each experiment
