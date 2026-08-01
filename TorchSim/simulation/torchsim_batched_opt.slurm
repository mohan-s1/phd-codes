#!/bin/bash
#SBATCH --account paolucci_standard
#SBATCH --output=orb.out      # Standard output file
#SBATCH --error=orb.err       # Standard error file
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a6000:1
#SBATCH --time=0-04:00:00
##SBATCH --mail-type=END
#SBATCH --no-requeue

module purge

module load gcc/14.2.0 openmpi/5.0.7 cuda/12.8.0 cudnn/9.8.0-CUDA-12.8.0 uv

uv run torchsim_orb_dispersion.py