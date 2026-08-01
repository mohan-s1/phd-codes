#!/bin/bash

module purge

INPUT="log.lammps"
OUTPUT="clean_log.lammps"

# Copy everything exactly as-is except lines matching the warning
grep -v '^WARNING: Pair style restartinfo set but has no restart support' "$INPUT" > "$OUTPUT"

module load uv

lammps_input="mace_gpu_nvt.lammps"
lammps_dumpfile="dump.lammpstrj"
xyz_file="Pd_CHA_650.xyz"
lammps_logfile="clean_log.lammps"
validation_path="validation"
number_of_structures=5
number_of_even_structures=5
frames_to_skip=500

uv run /project/paolucci/mace_validation/gamma_point/validate_mace_kelsey.py --lammps_input "${PWD}/${lammps_input}" \
--lammps_dumpfile "${PWD}/${lammps_dumpfile}" \
--xyz_file "${PWD}/${xyz_file}" \
--lammps_logfile "${PWD}/${lammps_logfile}" \
--validation_path "${PWD}/${validation_path}" \
--num_structs $number_of_structures \
--num_even_structs $number_of_even_structures \
--skip_n_frames $frames_to_skip \

# Paths to the SLURM script and python singlepoint file to copy
JOB1="/project/paolucci/mace_validation/gamma_point/run_vasp65_priority.slurm"
JOB2="/project/paolucci/mace_validation/gamma_point/singlepoint_pbe.py"

cd "${validation_path}"

for dir in */ ; do
  echo "Processing $dir"
  cd "$dir" || continue

  # Copy the SLURM scripts into the directory
  cp "$JOB1" .
  cp "$JOB2" .

  cd ../
done
