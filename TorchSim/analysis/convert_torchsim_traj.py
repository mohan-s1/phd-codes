# /// script
# requires-python = "==3.12.2"
# dependencies = [
#   "numpy",
#   "torch",
#   "torch-sim-atomistic",
#   "ase",
#   "mdanalysis",
# ]
# ///
# --------------------------------------------------------------------------------
## Import statements
import numpy as np
import torch_sim as ts
from ase.io import write
from ase import Atoms

# --------------------------------------------------------------------------------
## Define writer
def h5md_to_extxyz(h5md_file:str, xyz_file:str):
    """
    Converts .h5md file which is the standard TorchSim output to an extended .xyz 

    Args:
        h5md_file (str): path to .h5md file
        xyz_file (str): name (and path) to desired .xyz file
    """
    with ts.TorchSimTrajectory(h5md_file, mode="r") as traj:
        positions_all  = traj.get_array("positions")   # [n_frames, n_atoms, 3]
        forces_all     = traj.get_array("forces")      # [n_frames, n_atoms, 3]
        energies_all   = traj.get_array("potential_energy")  # [n_frames] or [n_frames, 1]
        atomic_numbers = traj.get_array("atomic_numbers").squeeze()    # [n_atoms] or [n_frames, 1]
        cell           = traj.get_array("cell")              # [3, 3] or [n_frames, 3, 3]

    n_frames = positions_all.shape[0]
    energies_all = np.array(energies_all).squeeze()  # flatten to [n_frames]

    # # cell may be stored once (NVT) or per-frame (NPT)
    # cell_per_frame = cell.ndim == 3

    # frames = []
    # for i in range(n_frames):
    #     cell_i = cell[i] if cell_per_frame else cell

    # cell may be stored once (NVT) or per-frame (NPT)
    cell_per_frame = cell.ndim == 3 and cell.shape[0] == n_frames
    cell_single = cell.squeeze(0) if cell.ndim == 3 else cell  # [3, 3] fallback

    frames = []
    for i in range(n_frames):
        cell_i = cell[i].transpose() if cell_per_frame else cell_single.transpose() 
    # the cell attribute has lattice vectors as columns, but we have to tranpose to row vectors to write out
        
        atoms = Atoms(
            numbers=atomic_numbers,
            positions=positions_all[i],
            cell=cell_i,
            pbc=True,
        )

        ## These go into the extxyz comment line as per-frame scalars
        atoms.info["energy"] = float(energies_all[i])

        ## Per-atom forces stored as an array attribute
        atoms.arrays["forces"] = np.array(forces_all[i])

        frames.append(atoms)

    write(xyz_file, frames, format="extxyz")
    print(f"Wrote {n_frames} frames to {xyz_file}")

# --------------------------------------------------------------------------------
## Call writer
h5md_to_extxyz(f"/path/to/input/filename.h5md", f"/path/to/output/filename.xyz")