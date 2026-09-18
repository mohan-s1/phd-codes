# /// script
# python = ">=3.10,<3.12"
# dependencies = [
#   "numpy",
#   "scipy",
#   "torch",
#   "mace-torch",
#   "ase",
#   "plumed",
# ]
# ///


import os
os.environ["PLUMED_KERNEL"] = "/project/paolucci/new_software/plumed-2.10.0/lib/libplumedKernel.so"

from ase.io import read
from ase.calculators.plumed import Plumed
from ase.md.nose_hoover_chain import NoseHooverChainNVT
from ase import units

from mace.calculators import MACECalculator
from ase.io.trajectory import Trajectory

import torch
import numpy as np
# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------

timestep = 0.5 * units.fs

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
# ------------------------------------------------------------
# Read the LAST configuration from the previous trajectory
# ------------------------------------------------------------


with Trajectory("md.traj") as old_traj:
    n_frames = len(old_traj)
    # atoms = old_traj[-1]              # or read("md.traj", index=-1)

previous_steps = n_frames * 100   # last fully-checkpointed step

atoms = read("md.traj", index=-1)

Al_indices = np.where(np.array(atoms.get_chemical_symbols()) == 'Al')[0]
Co_indices = np.where(np.array(atoms.get_chemical_symbols()) == 'Co')[0]

# <Al_ASE_idx, Co_ASE_idx> + 1
plumed_Al_index = Al_indices[0] + 1
plumed_Co_index = Co_indices[0] + 1

# Enable periodic boundary conditions in all three directions
atoms.set_pbc([True, True, True])

# Make sure the unit cell is present
print("Cell:", atoms.cell)
print("PBC:", atoms.pbc)

temperature_kelvin = 600
num_steps = 1_000_000
dump_frequency = 100

# ------------------------------------------------------------
# Base calculator
# ------------------------------------------------------------

base_calc = MACECalculator(model_paths=["Co_NH3_stagetwo_compiled.model"], device=device,)


# ------------------------------------------------------------
# PLUMED setup
# ------------------------------------------------------------

# setup = [
#     f"RESTART\n",

#     "d: DISTANCE ATOMS=289,583\n",

#     "metad: METAD "
#     "ARG=d "
#     "SIGMA=0.03 "
#     "HEIGHT=1.5 "
#     "PACE=500 "
#     "BIASFACTOR=10 "
#     "TEMP={} "
#     "GRID_MIN=0.2 "
#     "GRID_MAX=1.5 "
#     "GRID_BIN=500 "
#     "FILE=HILLS\n",

#     "PRINT ARG=d,metad.bias STRIDE=100 FILE=COLVAR\n",
# ]

setup = [
    "RESTART\n"
    f"d: DISTANCE ATOMS={plumed_Co_index},{plumed_Al_index}\n", 
    f"metad: METAD ARG=d SIGMA=0.03 HEIGHT=1.5 PACE=500 BIASFACTOR=10 TEMP={temperature_kelvin} GRID_MIN=0.1 GRID_MAX=2.0 GRID_BIN=400 FILE=HILLS\n",
    "PRINT ARG=d,metad.bias STRIDE=100 FILE=COLVAR\n",
]


# ------------------------------------------------------------
# PLUMED calculator
# ------------------------------------------------------------

calc = Plumed(
    calc=base_calc,
    input=setup,
    timestep=timestep,
    atoms=atoms,
    kT=temperature_kelvin * units.kB,
    log="plumed.log",
    restart=True,
)

# Tell ASE/PLUMED how many MD steps have already occurred.
calc.istep = previous_steps

atoms.calc = calc


# ------------------------------------------------------------
# Continue MD
# ------------------------------------------------------------

dyn = NoseHooverChainNVT(
    atoms,
    timestep=timestep,
    temperature_K=temperature_kelvin,
    tdamp=100 * units.fs,
)


# Append to the existing trajectory
from ase.io.trajectory import Trajectory

traj = Trajectory("md.traj", "a", atoms)
dyn.attach(traj.write, interval=dump_frequency)


# Run another 1,000,000 steps
dyn.run(num_steps)
