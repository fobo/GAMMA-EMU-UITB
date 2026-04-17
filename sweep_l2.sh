#!/bin/bash
# Sweep L2 buffer size

echo "Available models:"
echo "ALBERT_m alexnet BERT_m Densenet dlrmRMC1_m googlenet manual mnasnet"
echo "mobilenet_v2 nfc_m resnet18 resnet50 resnext50_32x4d shufflenet_v2"
echo "squeezenet T5_m transformer try vgg16 wide_resnet50"
read -p "Enter model name: " MODEL

L2_SIZES=(27000 54000 108000 216000 432000)
OUTDIR="sweep_l2_${MODEL}"
mkdir -p "$OUTDIR"
GAMMA_DIR="/mnt/c/ProjectGamma/GAMMA-EMU-UITB/src/GAMMA"
cd "$GAMMA_DIR" || { echo "Could not cd to $GAMMA_DIR"; exit 1; }
for L2 in "${L2_SIZES[@]}"; do
    RUN_NAME="${MODEL}_l2-${L2}"
    echo "Running: $RUN_NAME"
    python main.py \
        --model "$MODEL" \
        --fitness1 "latency" \
        --fitness2 "energy" \
        --num_pop 20 \
        --epochs 100 \
        --num_pe 1024 \
        --l1_size 512 \
        --l2_size "$L2" \
        --slevel_min 2 \
        --slevel_max 2 \
        --num_layer 2 \
        --log_level 1 \
        --outdir "${OUTDIR}/${RUN_NAME}"
    echo "Finished: $RUN_NAME"
    echo "---"
done

echo "L2 size sweep complete. Results in $OUTDIR"