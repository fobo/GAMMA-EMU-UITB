#!/bin/bash

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate gamma

BASE_DIR="$HOME/GAMMA-EMU-UITB"
LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

models=("mnasnet" "mobilenet_v2" "shufflenet_v2" "resnet18" "resnet50" "resnext50_32x4d" "Densenet" "googlenet" "ALBERT" "BERT_m" "T5_m" "transformer" "nfc_m" "dlrmRMC1_m" "alexnet" "vgg16")
sweeps=("./sweep_l1.sh" "./sweep_l2.sh" "./sweep_num_pe.sh" "./sweep_slevel.sh" "./sweep_num_pop.sh" "./sweep_fitness.sh")

cd "$BASE_DIR" || { echo "Failed to enter directory"; exit 1; }

sed -i "s|/home/${user}/|/home/${user}/|g" *.sh

echo "Starting Master Sweep in environment: $CONDA_DEFAULT_ENV"

for model in "${models[@]}"; do
    
    CSV_FILE="$LOG_DIR/${model}_metrics.csv"
    echo "Model,Sweep,Elapsed_Time(s),CPU_Usage(%),Peak_RAM(KB),Disk_Reads,Disk_Writes,Temp_Files_Created" > "$CSV_FILE"

    for sweep in "${sweeps[@]}"; do
        if [ ! -f "$sweep" ]; then
            echo "[$(date)] Skipping: $sweep (file missing)" | tee -a "$LOG_DIR/master_errors.log"
            continue
        fi

        echo "[$(date)] Starting $sweep for $model..."
        
        START_FILES=$(find "$BASE_DIR" -type f | wc -l)
        
        /usr/bin/time -o "$LOG_DIR/temp_metrics.txt" -f "%e,%P,%M,%I,%O" \
            bash -c "printf '%s\n' '$model' | bash '$sweep' >> '$LOG_DIR/${model}_${sweep#./}.log' 2>&1"
        
        if [ $? -ne 0 ]; then
            echo "[ERROR] $sweep failed for $model. Check $LOG_DIR/${model}_${sweep#./}.log" | tee -a "$LOG_DIR/master_errors.log"
        fi

        END_FILES=$(find "$BASE_DIR" -type f | wc -l)
        FILES_CREATED=$((END_FILES - START_FILES))

        if [ -f "$LOG_DIR/temp_metrics.txt" ]; then
            IFS=',' read -r ELAPSED CPU_PCT RAM_KB FS_IN FS_OUT < "$LOG_DIR/temp_metrics.txt"
            CPU_CLEAN=$(echo "$CPU_PCT" | tr -d '%')
            echo "$model,$sweep,$ELAPSED,$CPU_CLEAN,$RAM_KB,$FS_IN,$FS_OUT,$FILES_CREATED" >> "$CSV_FILE"
        else
            echo "Could not retrieve metrics for $sweep." | tee -a "$LOG_DIR/master_errors.log"
        fi
        
    done
done

rm -f "$LOG_DIR/temp_metrics.txt"
echo "Master sweep complete. Metrics saved to $LOG_DIR/ (one CSV per model)."
