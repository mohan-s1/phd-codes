#!/bin/bash
#SBATCH --account paolucci_standard
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=36
#SBATCH --time=0-08:00:00
#SBATCH --output=dft.out
#SBATCH -e dft.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mjs7eek@virginia.edu
#SBATCH --partition=parallel

module purge
export MODULEPATH=/project/paolucci/apps/modulefiles:$MODULEPATH

module load ase
module load intel/2025.0

module load vasp/6.5.0
unset VASP_SCRIPT
export VASP_COMMAND=/project/paolucci/mohan/setup_vasp65_gam.sh

python multi_bootstrap_pbe.py