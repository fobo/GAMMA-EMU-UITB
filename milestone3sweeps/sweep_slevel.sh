#!/bin/bash
# Sweep over all fitness1/fitness2 combinations

echo "Available models:"
echo "ALBERT_m alexnet BERT_m Densenet dlrmRMC1_m googlenet manual mnasnet"
echo "mobilenet_v2 nfc_m resnet18 resnet50 resnext50_32x4d shufflenet_v2"
echo "squeezenet T5_m transformer try vgg16 wide_resnet50"
read -p "Enter model name: " MODEL

FITNESS_OPTIONS=("latency" "energy" "power" "EDP" "area")
OUTDIR="sweep_fitness_${MODEL}"
mkdir -p "$OUTDIR"

for F1 in "${FITNESS_OPTIONS[@]}"; do
    for F2 in "${FITNESS_OPTIONS[@]}"; do
        if [ "$F1" == "$F2" ]; then
            continue
        fi
        RUN_NAME="${MODEL}_f1-${F1}_f2-${F2}"
        echo "Running: $RUN_NAME"
        python main.py \
            --model "$MODEL" \
            --fitness1 "$F1" \
            --fitness2 "$F2" \
            --num_pop 20 \
            --epochs 100 \
            --num_pe 1024 \
            --l1_size 512 \
            --l2_size 108000 \
            --slevel_min 2 \
            --slevel_max 2 \
            --num_layer 2 \
            --log_level 1 \
            --outdir "${OUTDIR}/${RUN_NAME}"
        echo "Finished: $RUN_NAME"
        echo "---"
    done
done

echo "Fitness sweep complete. Results in $OUTDIR"