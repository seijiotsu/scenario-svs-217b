#!/usr/bin/env python

''' Generate a bash script based on experiments '''

''' Meta-parameters to be set up '''
# Generated file path, MUST BE INSIDE OF scenario-svs folder
import cmd


GENFILEPATH = './generated_exps.sh'
# the backslah at the end is important
LOGPATH = './exp_log_files/'

# How many processes to run in parallel
PERGROUP = 64

# N by N grid, each element stands for N
TOPO_LIST = [4, 8]

# Packet Loss or not
# TODO: according to our last discussion, set up a high drop-rate, maybe try something different
DROP_RATE = [0, 0.5]

# Fast publishers
# TODO: according to our last discussion, set up 1) All frequent, 2) All infrequent, 3) 10% frequent
FAST_PUB = []

for x in TOPO_LIST:
    n = int(x**2)
    FAST_PUB.append([0, int(n*0.1), int(n*0.2), int(n*0.3), int(n*0.4), int(n*0.5), int(n*0.6)])

# Frag or not, if false then there we just send out the whole sync-interest
FRAG = [True, False]

# Various method to test if FRAG is set to True
METHODS = ['FULL', 'RAND', 'RAND_RECENT']

# Add extra for #recent
RECENT_EXTRA = 5

# Inter Slow/Fast
INTER_SLOW = 1000
INTER_FAST = 100

# Seconds to stop
SEC_STOP = 10







def gen_script():
    # Cmd lisit
    cmdList = []

    # To include in sh
    head = '#!/bin/sh'
    build = ''
    prefix = './build/large-grid '
    suffixMethod = '_Method '
    suffixRow = '_Row '
    suffixCol = '_Col '
    suffixPub = '_Nodes_Pub_Fast '
    intSlowSuf, intFastSuf, secStopSuf = '_MS_INTER_SLOW ', '_MS_INTER_FAST ', '_S_STOP '
    recentSuf, randomSuf = '_RECENT_PUB ', '_RANDOM_PUB '
    dropRateSuf = '_DROP_RATE'
    mtuSuf = '_MTU'


    def gen_line(N, intSlow, intFast, fastPub, recentIncl, randIncl, secStop, dropRate, method, MTU = -1):
        mid = str(N) + suffixRow + str(N) + suffixCol \
            + str(intSlow) + intSlowSuf + str(intFast) + intFastSuf \
            + str(fastPub) + suffixPub + str(recentIncl) + recentSuf + str(randIncl) + randomSuf \
            + str(secStop) + secStopSuf + str(dropRate) + dropRateSuf
        if MTU != -1:
            mid += ' ' + str(MTU) + mtuSuf

        log_prefix =  method + suffixMethod

        return (prefix + mid + ' > ' + LOGPATH + (log_prefix + mid).replace(' ', '-') + '.log &')



    for topoN, fastPubGroup in zip(TOPO_LIST, FAST_PUB):
        grid_size = topoN ** 2
        mtu = int(grid_size * 0.3)
        for numFastPub in fastPubGroup:
            for frag in FRAG:
                if frag:
                    for dr in DROP_RATE:
                        for m in METHODS:
                            if m == 'FULL':
                                # Baseline(frag): still send out entire states, fragmented
                                cmdList.append(gen_line(topoN, INTER_SLOW, INTER_FAST,
                                        numFastPub, 0, 99999, SEC_STOP, dr, m, mtu))
                            elif m == 'RAND':
                                # Random, only send out SINGLE interest, size == mtu
                                cmdList.append(gen_line(topoN, INTER_SLOW, INTER_FAST,
                                        numFastPub, 0, mtu, SEC_STOP, dr, m))
                            else:
                                # Mix: recent = freq + RECENT_EXTRA, rest is random
                                if numFastPub == grid_size:
                                    # All frequent
                                    cmdList.append(gen_line(topoN, INTER_SLOW, INTER_FAST,
                                            numFastPub, mtu, 0, SEC_STOP, dr, m))
                                else:
                                    numRecent = max(min(numFastPub + RECENT_EXTRA, mtu - 5), 2)
                                    cmdList.append(gen_line(topoN, INTER_SLOW, INTER_FAST,
                                            numFastPub, numRecent, (mtu - numRecent),
                                            SEC_STOP, dr, m))
                else:
                    for dr in DROP_RATE:
                        cmdList.append(gen_line(topoN, INTER_SLOW, INTER_FAST,
                                numFastPub, 0, 99999, SEC_STOP, dr, "BASE"))


    # Process lines:
    cmdLinesProcessed = []
    cmdLinesProcessed.append(head)
    cmdLinesProcessed.append('\n\n')
    cmdLinesProcessed.append('./waf configure')
    cmdLinesProcessed.append('./waf')
    cmdLinesProcessed.append('mkdir -p ' + LOGPATH)
    cmdLinesProcessed.append('\n\n')
    cmdLinesProcessed += [x for y in (cmdList[i:i+PERGROUP] + ['wait'] * (i < len(cmdList) - (PERGROUP - 1)) for \
                i in range(0, len(cmdList), PERGROUP)) for x in y]


    with open(GENFILEPATH, 'w+') as f:
        f.writelines(l + '\n' for l in cmdLinesProcessed)



if __name__ == '__main__':
    gen_script()