#!/bin/bash
# Sweep: l1_size (local buffer size per PE)
# All other parameters held at baseline

OUTDIR="gamma_results_sweep_l1"

for L1 in 64 128 256 512 1024 2048; do
    echo "Run: l1_size=$L1"
    cd ./src/GAMMA
    python main.py --fitness1 latency --fitness2 power --num_pe 168 \
                  --l2_size 108000 --NocBW 81920000 \
                  --epochs 100 --num_pop 20 --l1_size $L1 \
                  --model vgg16 --singlelayer 1 \
                  --outdir $OUTDIR
    cd ../../
done
