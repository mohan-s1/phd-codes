#!/bin/bash
#SBATCH --account paolucci_standard
#SBATCH --output=mace_nvt.out      # Standard output file
#SBATCH --error=mace_nvt.err       # Standard error file
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a6000:1
#SBATCH --time=0-20:00:00
##SBATCH --mail-type=END
#SBATCH --no-requeue

module purge

module load gcc/14.2.0 openmpi/5.0.7 cuda/12.8.0 cudnn/9.8.0-CUDA-12.8.0 cmake/4.1.2 imkl/2025.0.1

export LAMMPS_ROOT=/project/paolucci/new_software/lammps_gpu/build-ampere # point to `liblammps.so.0`
export LIBTORCH_ROOT=/project/paolucci/new_software/libtorch-gpu # point to `libtorch.so`

export LD_LIBRARY_PATH=$LAMMPS_ROOT/lib64:$LIBTORCH_ROOT/lib:$LD_LIBRARY_PATH

/project/paolucci/new_software/lammps_gpu/build-ampere/bin/lmp -k on g 1 -sf kk -pk kokkos newton on neigh half -in mace_gpu_nvt.lammps 

echo "finish!"