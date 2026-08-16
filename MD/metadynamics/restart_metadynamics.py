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
# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------

timestep = 0.5 * units.fs
temperature = 648

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

# ------------------------------------------------------------
# Base calculator
# ------------------------------------------------------------

base_calc = MACECalculator(model_paths=["Co_NH3_stagetwo_compiled.model"], device=device,)


# ------------------------------------------------------------
# PLUMED setup
# ------------------------------------------------------------

setup = [
    "RESTART\n",

    "d: DISTANCE ATOMS=289,583\n",

    "metad: METAD "
    "ARG=d "
    "SIGMA=0.03 "
    "HEIGHT=1.5 "
    "PACE=500 "
    "BIASFACTOR=10 "
    "TEMP=648 "
    "GRID_MIN=0.2 "
    "GRID_MAX=1.5 "
    "GRID_BIN=500 "
    "FILE=HILLS\n",

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
    kT=temperature * units.kB,
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
    temperature_K=temperature,
    tdamp=100 * units.fs,
)


# Append to the existing trajectory
from ase.io.trajectory import Trajectory

traj = Trajectory("md.traj", "a", atoms)
dyn.attach(traj.write, interval=100)


# Run another 1,000,000 steps
dyn.run(1_000_000)