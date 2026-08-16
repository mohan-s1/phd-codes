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
os.environ["PLUMED_KERNEL"]="/project/paolucci/new_software/plumed-2.10.0/lib/libplumedKernel.so"

from ase.io import read
from ase.calculators.plumed import Plumed
from ase.md.nose_hoover_chain import NoseHooverChainNVT
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.velocitydistribution import Stationary, ZeroRotation
from ase import units

# --- your existing base calculator (ML potential, DFT, etc.) ---
from mace.calculators import MACECalculator
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

base_calc = MACECalculator(model_paths=["Co_NH3_stagetwo_compiled.model"], device=device)

atoms = read('extended_CoNH3x4_MFI.cif')

# with open('plumed.dat') as f:
#    setup = f.readlines()

# <Co_ASE_idx, Al_ASE_idx> + 1
setup = [
    "d: DISTANCE ATOMS=289,583\n", 
    "metad: METAD ARG=d SIGMA=0.03 HEIGHT=1.5 PACE=500 BIASFACTOR=10 TEMP=648 GRID_MIN=0.2 GRID_MAX=1.5 GRID_BIN=500 FILE=HILLS\n",
    "PRINT ARG=d,metad.bias STRIDE=100 FILE=COLVAR\n",
]

timestep = 0.5 * units.fs

calc = Plumed(
    calc=base_calc,
    input=setup,
    timestep=timestep,
    atoms=atoms,
    kT=648 * units.kB,
    log='plumed.log',
    restart=False,
)
atoms.calc = calc

MaxwellBoltzmannDistribution(atoms, temperature_K=648)
Stationary(atoms)
ZeroRotation(atoms)

dyn = NoseHooverChainNVT(
    atoms,
    timestep=timestep,
    temperature_K=648,
    tdamp=100 * units.fs,   # thermostat relaxation time
    )

from ase.io.trajectory import Trajectory
traj = Trajectory('md.traj', 'w', atoms)
dyn.attach(traj.write, interval=100)
dyn.attach(lambda: None, interval=100)  # placeholder for your own logging/traj writer
dyn.run(1_000_000)  # 