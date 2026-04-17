#!/bin/bash
# Sweep: l2_size (global buffer size)
# All other parameters held at baseline

OUTDIR="gamma_results_sweep_l2"

for L2 in 27000 54000 108000 216000 432000; do
    echo "Run: l2_size=$L2"
    cd ./src/GAMMA
    python main.py --fitness1 latency --fitness2 power --num_pe 168 \
                  --l1_size 512 --NocBW 81920000 \
                  --epochs 100 --num_pop 20 --l2_size $L2 \
                  --model vgg16 --singlelayer 1 \
                  --outdir $OUTDIR
    cd ../../
done
