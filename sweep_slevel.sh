#!/bin/bash
# Sweep: slevel_min and slevel_max (parallelization levels)
# All other parameters held at baseline
# Note: slevel_min must be <= slevel_max

OUTDIR="gamma_results_sweep_slevel"

# Format: "slevel_min slevel_max"
SLEVEL_PAIRS=(
    "1 1"
    "1 2"
    "2 2"
    "1 3"
    "2 3"
    "3 3"
	"2 6"
)

for PAIR in "${SLEVEL_PAIRS[@]}"; do
    SMIN=$(echo $PAIR | cut -d' ' -f1)
    SMAX=$(echo $PAIR | cut -d' ' -f2)
    echo "Run: slevel_min=$SMIN, slevel_max=$SMAX"
    cd ./src/GAMMA
    python main.py --fitness1 latency --fitness2 power --num_pe 168 \
                  --l1_size 512 --l2_size 108000 --NocBW 81920000 \
                  --epochs 100 --num_pop 20 \
                  --slevel_min $SMIN --slevel_max $SMAX \
                  --model vgg16 --singlelayer 1 \
                  --outdir $OUTDIR
    cd ../../
done
