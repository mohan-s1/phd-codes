#!/bin/bash
#SBATCH --job-name=mace-train
#SBATCH --account=paolucci_standard
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a6000:1
#SBATCH --mem=64G              # typical full-GPU node memory
#SBATCH --time=0-06:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --mail-user=mjs7eek@virginia.edu
#SBATCH --mail-type=ALL

# ---------------------------------------------------
# Activate your MACE environment (no module load!)
# ---------------------------------------------------
module purge 
module load uv
source ~/mace_env/bin/activate

# ---------------------------------------------------
# Diagnostics block
# ---------------------------------------------------
echo "=== JOB STARTED ON $(hostname) at $(date) ==="
echo "=== GPU INFO ==="
nvidia-smi
# ---------------------------------------------------
# Go to the submission directory
# ---------------------------------------------------
cd $SLURM_SUBMIT_DIR
# ---------------------------------------------------           
python mace_train.py