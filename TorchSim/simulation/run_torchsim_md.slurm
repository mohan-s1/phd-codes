#!/bin/bash
#SBATCH --account paolucci
#SBATCH --output=torchsim_md.out      # Standard output file
#SBATCH --error=torchsim_md.err       # Standard error file
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a6000:1
#SBATCH --time=0-00:30:00
#SBATCH --mail-type=END
#SBATCH --no-requeue

module purge

module load gcc/14.2.0 openmpi/5.0.7 cuda/12.8.0 cudnn/9.8.0-CUDA-12.8.0 uv

source ~/uv_mlp/bin/activate

uv run torchsim_md.py