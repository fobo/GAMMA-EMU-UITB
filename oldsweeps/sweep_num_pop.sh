#!/bin/bash
# Sweep: num_pop (population size)
# All other parameters held at baseline

OUTDIR="gamma_results_sweep_pop"

for POP in 5 10 20 40 80 160; do
    echo "Run: num_pop=$POP"
    cd ./src/GAMMA
    python main.py --fitness1 latency --fitness2 power --num_pe 168 \
                  --l1_size 512 --l2_size 108000 --NocBW 81920000 \
                  --epochs 100 --num_pop $POP \
                  --model vgg16 --singlelayer 1 \
                  --outdir $OUTDIR
    cd ../../
done
