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
