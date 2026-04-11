#!/bin/bash

OUTDIR="gamma_results"

for i in $(seq 1 20); do
    EPOCHS=$((i * 10))
    
    echo "Run $i: epochs=$EPOCHS, outdir=$OUTDIR"
    
    cd ./src/GAMMA
    python main.py --fitness1 latency --fitness2 power --num_pe 168 --l1_size 512 --l2_size 108000 --NocBW 81920000 \
                  --epochs $EPOCHS \
                  --model vgg16 --singlelayer 1 \
                  --outdir $OUTDIR
    cd ../../
done