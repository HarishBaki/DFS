#!/bin/bash
#SBATCH --job-name=conus404_daily
#SBATCH --output=slurmout/conus404-%A_%a.out
#SBATCH --error=slurmout/conus404-%A_%a.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6

# --- Activate conda ---
source /network/rit/lab/basulab/Anaconda3/etc/profile.d/conda.sh
conda activate conus404

# ============================================================
# Arguments:
#   $1 = START_DATE or missing_dates file
#   $2 = MODE (optional: "single" | "array" | "file")
#
# Usage examples:
#   sbatch jobsub_conus_download.slurm 1980-07-15 single
#   sbatch --array=0-364 jobsub_conus_download.slurm 1980-01-01 array
#   sbatch --array=0-52 jobsub_conus_download.slurm missing_dates_all.txt file
# ============================================================

INPUT=$1
MODE=${2:-array}   # default = array mode

if [ -z "$INPUT" ]; then
    echo "Usage: $0 START_DATE|missing_dates.txt [single|array|file]"
    exit 1
fi

# --- Determine DATE based on mode ---
if [ "$MODE" == "single" ]; then
    # Run for exactly one day
    DATE=$INPUT

elif [ "$MODE" == "array" ]; then
    # Serial incrementing with START_DATE + offset
    DATE=$(date -d "${INPUT} +${SLURM_ARRAY_TASK_ID} days" +%Y-%m-%d)

elif [ "$MODE" == "file" ]; then
    # Read date from file based on SLURM_ARRAY_TASK_ID
    DATE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" "$INPUT")

    if [ -z "$DATE" ]; then
        echo "No date found in $INPUT for SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID"
        exit 1
    fi

else
    echo "Invalid mode: $MODE"
    echo "Valid modes: single | array | file"
    exit 1
fi

echo "=========================================================="
echo "Running CONUS404 download"
echo "Mode: $MODE"
echo "Date: $DATE"
echo "Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "=========================================================="

python conus404_daily_downloader.py --date "$DATE"