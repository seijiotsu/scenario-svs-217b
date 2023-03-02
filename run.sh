#!/bin/bash

if [ -z "$1" ]
then
	echo "argument not provided"
	exit 1
fi

rm -rf results/$1
mkdir -p results/$1

for slow in 5000 3000 2000 1000 500
do
	./build/large-grid $slow 4 8 > results/$1/$slow.log &
done
