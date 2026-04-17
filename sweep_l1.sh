#!/bin/bash
# Sweep over all fitness1/fitness2 combinations
GAMMA_DIR="/mnt/c/ProjectGamma/src/GAMMA"



echo "Available models:"
echo "ALBERT_m alexnet BERT_m Densenet dlrmRMC1_m googlenet manual mnasnet"
echo "mobilenet_v2 nfc_m resnet18 resnet50 resnext50_32x4d shufflenet_v2"
echo "squeezenet T5_m transformer try vgg16 wide_resnet50"
read -p "Enter model name: " MODEL

L1_SIZES=(64 128 256 512 1024 2048)
OUTDIR="sweep_l1_${MODEL}"
mkdir -p "$OUTDIR"
GAMMA_DIR="/mnt/c/ProjectGamma/GAMMA-EMU-UITB/src/GAMMA"
cd "$GAMMA_DIR" || { echo "Could not cd to $GAMMA_DIR"; exit 1; }
for L1 in "${L1_SIZES[@]}"; do
    RUN_NAME="${MODEL}_l1-${L1}"
    echo "Running: $RUN_NAME"
    python main.py \
        --model "$MODEL" \
        --fitness1 "latency" \
        --fitness2 "energy" \
        --num_pop 20 \
        --epochs 100 \
        --num_pe 1024 \
        --l1_size "$L1" \
        --l2_size 108000 \
        --slevel_min 2 \
        --slevel_max 2 \
        --num_layer 2 \
        --log_level 1 \
        --outdir "${OUTDIR}/${RUN_NAME}"
    echo "Finished: $RUN_NAME"
    echo "---"
done

echo "L1 size sweep complete. Results in $OUTDIR"