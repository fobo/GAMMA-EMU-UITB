#!/bin/bash
# Sweep: num_pe (number of Processing Elements)
# All other parameters held at baseline

OUTDIR="gamma_results_sweep_pe"

for PE in 64 128 168 256 512 1024; do
    echo "Run: num_pe=$PE"
    cd ./src/GAMMA
    python main.py --fitness1 latency --fitness2 power \
                  --l1_size 512 --l2_size 108000 --NocBW 81920000 \
                  --epochs 100 --num_pop 20 --num_pe $PE \
                  --model vgg16 --singlelayer 1 \
                  --outdir $OUTDIR
    cd ../../
done
