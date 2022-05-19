#!/bin/bash

mkdir -p results/$1

for slow in 5000 3000 2000 1000 500
do
	./build/large-grid $slow > results/$1/$slow.log
done
