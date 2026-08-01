# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "numpy",
#   "torch",
#   "torch-sim-atomistic",
#   "mace-torch",
#   "orb-models",
#   "ase",
# ]
# ///
# --------------------------------------------------------------------------------
## Import statements; currently defaults to Orb wrapped in D3(BJ) corrections
import time
import torch
import torch_sim as ts
from ase.io import read

from torch_sim.models.orb import OrbModel
from orb_models.forcefield import pretrained
from orb_models.forcefield.inference.d3_model import D3SumModel, AlchemiDFTD3

import pickle
# --------------------------------------------------------------------------------
## Import statements
start = time.perf_counter()

device = "cuda"
CHUNK_SIZE = 100  # reduce this if you get out of memory (OOM) error

orbff, atoms_adapter = pretrained.orb_v3_conservative_inf_omat(
    device=device,
    precision="float32-high",
)

orbff_d3 = D3SumModel(orbff, AlchemiDFTD3(functional="PBE", damping="BJ", compile=True))

ts_model = OrbModel(orbff_d3, atoms_adapter) # change to OrbModel(orbff, atoms_adapter) if you don't want dispersion corrections

all_structures = read("FILENAME.xyz", index=":") # TODO: change name to read in structures here

print(f"Loaded {len(all_structures)} structures")
for atoms in all_structures:
    atoms.pbc = True

# ── Chunk and process ─────────────────────────────────────────────────────────
all_energies = {}

for chunk_start in range(0, len(all_structures), CHUNK_SIZE):
    chunk = all_structures[chunk_start : chunk_start + CHUNK_SIZE]
    chunk_indices = list(range(chunk_start, chunk_start + len(chunk)))
    print(f"Processing structures {chunk_start}-{chunk_start + len(chunk) - 1}...")

    ts_state = ts.io.atoms_to_state(chunk, device=device, dtype=torch.float32)

    relaxed_state = ts.optimize(
        system=ts_state,
        model=ts_model, # the model can be changed to any other Orb or MACE model 
        optimizer=ts.Optimizer["fire"],
        convergence_fn=ts.generate_force_convergence_fn(force_tol=0.1, include_cell_forces=False),
        max_steps=200,
        autobatcher=True,
        steps_between_swaps=10,
    )

    final_state = ts.optimize(
        system=relaxed_state,
        model=ts_model,  # the model can be changed to any other Orb or MACE model 
        optimizer=ts.Optimizer["fire"],
        convergence_fn=ts.generate_force_convergence_fn(force_tol=0.03, include_cell_forces=False),
        max_steps=200,
        autobatcher=True,
        steps_between_swaps=10,
    )

    results = ts_model(final_state)
    chunk_energies = results["energy"].cpu().tolist()

    for idx, energy in zip(chunk_indices, chunk_energies):
        all_energies[idx] = energy

    # Free GPU memory before the next chunk
    del ts_state, relaxed_state, final_state, results
    torch.cuda.empty_cache()

# --------------------------------------------------------------------------------
## Sort energies, print, and save to .pkl file
sorted_energies = dict(sorted(all_energies.items(), key=lambda x: x[1]))
print("\nSorted energies:")
print(sorted_energies)

with open("FILENAME.pkl", "wb") as file: # TODO: change .pkl filename as needed
    pickle.dump(sorted_energies, file)

print("pkl file saved.")

end = time.perf_counter()
print(f"Elapsed time: {end - start:.4f} seconds")