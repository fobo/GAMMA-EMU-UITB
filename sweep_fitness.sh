#!/bin/bash
# Sweep: fitness1/fitness2 combinations
# All other parameters held at baseline

OUTDIR="gamma_results_sweep_fitness"

FITNESS_PAIRS=(
    "latency power"
    "latency energy"
    "latency EDP"
    "latency area"
    "energy power"
    "energy EDP"
)

for PAIR in "${FITNESS_PAIRS[@]}"; do
    F1=$(echo $PAIR | cut -d' ' -f1)
    F2=$(echo $PAIR | cut -d' ' -f2)
    echo "Run: fitness1=$F1, fitness2=$F2"
    cd ./src/GAMMA
    python main.py --fitness1 $F1 --fitness2 $F2 --num_pe 168 \
                  --l1_size 512 --l2_size 108000 --NocBW 81920000 \
                  --epochs 100 --num_pop 20 \
                  --model vgg16 --singlelayer 1 \
                  --outdir $OUTDIR
    cd ../../
done
