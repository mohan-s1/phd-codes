## --------------------------------------------------------------------------------
## import MLP packages
from mace.calculators import mace_mp
import torch
import torch_sim as ts
from torch_sim.units import MetalUnits as Units
from torch_sim.models.mace import MaceModel
## --------------------------------------------------------------------------------
## import ASE
from ase.optimize import FIRE, LBFGS
from ase.io import read, write
from torchmetrics import Metric
## --------------------------------------------------------------------------------
## import MLP packages

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


device_str = "cuda" if torch.cuda.is_available() else "cpu"  # string version for MACE

dtype = torch.float32

mace_ase = mace_mp(model="cummins_combined_stagetwo.model", device=device_str)
mace_raw = mace_mp(model="cummins_combined_stagetwo.model", device=device_str, return_raw_model=True)

mace_model = MaceModel(model=mace_raw, device=device)

structure = read("POSCAR_CHA_H2O_filled")

structure.set_pbc([True, True, True])  # ensure all dims are periodic

## Relax forces on initial structure
#structure.calc = mace_ase

#dyn = FIRE(structure)

#dyn.run(fmax=0.1)

## Begin MD routine
trajectory_files = [f"Cu_traj.h5md"]

final_state = ts.integrate(
    system=structure,
    model=mace_model,
    n_steps=10000,
    timestep=0.0005, # 0.5 ps
    temperature=473, # Kelvin
    integrator=ts.Integrator.nvt_nose_hoover,
    trajectory_reporter=dict(filenames=trajectory_files, state_frequency=10, state_kwargs={
            "save_forces": True,
            "save_velocities": False,   # set True if you want these too
            "variable_cell": False,     # set True if running NPT
        }),
)
final_atoms_list = final_state.to_atoms()

# extract the final energy from the trajectory file
final_energies = []
for filename in trajectory_files:
    with ts.TorchSimTrajectory(filename) as traj:
        final_energies.append(traj.get_array("potential_energy")[-1])

print(final_energies)