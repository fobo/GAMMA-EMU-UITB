#!/bin/bash
# Sweep parallelization level pairs (slevel_min, slevel_max)

echo "Available models:"
echo "ALBERT_m alexnet BERT_m Densenet dlrmRMC1_m googlenet manual mnasnet"
echo "mobilenet_v2 nfc_m resnet18 resnet50 resnext50_32x4d shufflenet_v2"
echo "squeezenet T5_m transformer try vgg16 wide_resnet50"
read -p "Enter model name: " MODEL

SLEVEL_PAIRS=(
    "1 1"
    "1 2"
    "2 2"
    "1 3"
    "2 3"
    "3 3"
    "2 6"
)
OUTDIR="sweep_slevel_${MODEL}"
mkdir -p "$OUTDIR"
GAMMA_DIR="/mnt/c/ProjectGamma/GAMMA-EMU-UITB/src/GAMMA"
cd "$GAMMA_DIR" || { echo "Could not cd to $GAMMA_DIR"; exit 1; }
for PAIR in "${SLEVEL_PAIRS[@]}"; do
    SMIN=$(echo "$PAIR" | awk '{print $1}')
    SMAX=$(echo "$PAIR" | awk '{print $2}')
    RUN_NAME="${MODEL}_slevel-${SMIN}-${SMAX}"
    echo "Running: $RUN_NAME"
    python main.py \
        --model "$MODEL" \
        --fitness1 "latency" \
        --fitness2 "energy" \
        --num_pop 20 \
        --epochs 100 \
        --num_pe 1024 \
        --l1_size 512 \
        --l2_size 108000 \
        --slevel_min "$SMIN" \
        --slevel_max "$SMAX" \
        --num_layer 2 \
        --log_level 1 \
        --outdir "${OUTDIR}/${RUN_NAME}"
    echo "Finished: $RUN_NAME"
    echo "---"
done

echo "Slevel sweep complete. Results in $OUTDIR"