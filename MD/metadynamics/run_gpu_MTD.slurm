#!/bin/bash
#SBATCH --account=paolucci_standard
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a6000:1
#SBATCH --time=1-00:00:00
#SBATCH --output=MTD.out
#SBATCH --error=MTD.err
#SBATCH --mail-user=mjs7eek@virginia.edu

module purge

module load gcc openmpi uv cuda/12.8.0 cudnn/9.8.0-CUDA-12.8.0

export PATH=/project/paolucci/new_software/plumed-2.10.0/bin:$PATH

export LD_LIBRARY_PATH=/project/paolucci/new_software/plumed-2.10.0/lib:$LD_LIBRARY_PATH

export PLUMED_KERNEL=/project/paolucci/new_software/plumed-2.10.0/lib/libplumedKernel.so

uv run restart_metadynamics.py