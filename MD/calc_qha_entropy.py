# /// script
# python = ">=3.10,<3.12"
# dependencies = [
#   "numpy",
#   "scipy",
#   "matplotlib",
#   "ase",
# ]
# ///

from ase.io import read
from ase.geometry import wrap_positions
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------------
# Constants and parameters
kB = 1.3806504e-23 # J/K
h_Planck = 6.62607015e-34 # J*s
R = 8.314 # J/mol*K
temperature = 300 # K
symmetry = 4 # symmetry number for species at hand; 4 for square planar metal-ligand complexes as an example

# Read full trajectory ONCE
infile = f"/path/to/file.xyz" # can be any file type ASE can read; you should leave only the species whose entropy you want in the traj

full_traj = read(infile, ":")

print(len(full_traj))

# Total mass (constant)
total_mass = np.sum(full_traj[0].get_masses())
# --------------------------------------------------------------------------------
def compute_entropy(atom_list):

    # ================= ROTATIONAL =================
    I = np.zeros((len(atom_list), 3))

    for count, atoms in enumerate(atom_list):
        atoms = atoms.copy()
        atoms.center()
        I[count] = atoms.get_moments_of_inertia(vectors=0)

    I2 = I * 1.660539e-47 # convert from AMU to kg

    S_rot = R * np.log(
        8 * np.pi**2 / symmetry
        * np.sqrt(np.prod(np.average(I2, axis=0)))
        * (2 * np.pi * np.exp(1) * kB * temperature / h_Planck**2) ** (3 / 2)
    )

    # ================= VIBRATIONAL =================
    n_frames = len(atom_list)
    n_atoms = len(atom_list[0])
    n_coords = 3 * n_atoms

    masses = atom_list[0].get_masses()
    mass_vector = np.repeat(masses, 3)

    positions = np.zeros((n_frames, n_atoms, 3))
    cell = atom_list[0].get_cell()
    pbc = atom_list[0].get_pbc()

    for i, atoms in enumerate(atom_list):
        pos = wrap_positions(atoms.get_positions(), cell, pbc=pbc)
        positions[i] = pos

    flat_positions = positions.reshape(n_frames, n_coords)
    mean_structure = np.mean(flat_positions, axis=0)
    fluctuations = flat_positions - mean_structure

    weighted_fluctuations = fluctuations * np.sqrt(mass_vector)

    cov = np.cov(weighted_fluctuations, rowvar=False)

    eigenvalues = np.linalg.eigvalsh(cov)
    eigenvalues = np.sort(eigenvalues)

    vibrational_eigenvalues = eigenvalues[6:]
    vibrational_eigenvalues_si = vibrational_eigenvalues * 1.660539e-47 # convert from AMU to kg

    frequencies = np.sqrt((kB * temperature) / vibrational_eigenvalues_si)

    c_cm_s = 2.99792458e10 # speed of light in cm/s
    wavenumbers = frequencies / (2 * np.pi * c_cm_s)

    filtered_frequencies = frequencies[wavenumbers > 100]

    theta = (h_Planck * filtered_frequencies) / kB

    S_vib = R * np.sum(
        (theta / temperature) / (np.exp(theta / temperature) - 1)
        - np.log(1 - np.exp(-theta / temperature))
    )

    # ================= TRANSLATIONAL =================
    com_positions = np.zeros((n_frames, 3))

    for i, atoms in enumerate(atom_list):
        atoms = atoms.copy()
        atoms.set_positions(
            wrap_positions(atoms.get_positions(), cell=cell, pbc=pbc)
        )
        com_positions[i] = atoms.get_center_of_mass()

    deviations = com_positions - np.mean(com_positions, axis=0)
    cov_com = np.cov(deviations, rowvar=False)
    eigenvalues_com = np.linalg.eigvalsh(cov_com)

    principal_rmsfs = np.sqrt(eigenvalues_com)

    S_trans = R * np.log(
        ((24 * np.pi * np.exp(1) * total_mass * 1.66054e-27 * kB * temperature)
         / (h_Planck**2)) ** (3 / 2)
        * (np.prod(principal_rmsfs) * 1e-30)
    )

    return S_rot, S_vib, S_trans, S_rot + S_vib + S_trans


# --------------------------------------------------------------------------------
## Single run
# use_last_n_frames = 5000
# atom_subset = full_traj[-use_last_n_frames:]

# S_rot, S_vib, S_trans, S_tot = compute_entropy(atom_subset)
# --------------------------------------------------------------------------------
# Convergence study analagous to block averaging

slice_step = 1000 # Consider every n steps for convergence study 
max_frames = len(full_traj)

slices = np.arange(50, max_frames, slice_step)

total_entropy = []

rotational_entropy = []

translational_entropy = []

vibrational_entropy = []

slice_value = []

for frame_range in slices[::-1]:
    print(f"Using last {frame_range} frames")

    atom_subset = full_traj[-frame_range:]

    S_rot, S_vib, S_trans, S_tot = compute_entropy(atom_subset)

    slice_value.append(frame_range)
    
    total_entropy.append(S_tot)
    
    rotational_entropy.append(S_rot)
    
    translational_entropy.append(S_trans)

    vibrational_entropy.append(S_vib)

# --------------------------------------------------------------------------------
## Plot
Plas = plt.cm.plasma(np.linspace(0.25,0.99,4)) # color

delta_t = 0.0005  # assumed to be picoseconds

dump_frequency = 100

total_frames = len(full_traj)

simulation_time = np.linspace(0, total_frames, len(slices)) * delta_t * dump_frequency  # units of ps

marker_size = 10

plt.figure(figsize=(10, 6))

plt.plot(simulation_time, total_entropy[::-1], marker = "X", color = "k", markersize=marker_size, label = "Total")
plt.plot(simulation_time, rotational_entropy[::-1], marker = "^", mec='k', color = Plas[0], markersize=marker_size, label = "Rotation")
plt.plot(simulation_time, translational_entropy[::-1], marker = "s", mec='k', color = Plas[1], markersize=marker_size, label = "Translation")
plt.plot(simulation_time, vibrational_entropy[::-1], marker = "o", mec='k', color = Plas[2], markersize=marker_size, label = "Vibration")

ax = plt.gca()

# Make axis spines (lines) bold
for spine in ax.spines.values():
    spine.set_linewidth(2)

# Make tick lines and labels bold
ax.tick_params(axis='both', which='major', labelsize=14, width=2, length=6)
ax.tick_params(axis='both', which='minor', width=2, length=4)

# Bold the tick numbers
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('bold')

plt.xlabel("Cumulative MD Time Used / ps", weight="bold", fontsize=14)

plt.ylabel(r"Entropy / $\mathbf{ J \; (mol \cdot K)^{-1} }$", weight="bold", fontsize=16)

plt.legend(frameon = False, prop={'weight': 'bold', 'size': 14}, bbox_to_anchor=(1.4, 1),
           title=f'Entropy at {temperature} K', title_fontproperties = {'weight': 'bold', 'size': 16})

plt.tight_layout()

plt.show();

# --------------------------------------------------------------------------------
## Uncomment below to print out averge and StDev of individual and cumulative entropy 

# target_time = max(simulation_time * 0.7) # average over last ~70% of trajectory

# closest_index = (np.abs(simulation_time - target_time)).argmin()

# n = closest_index

# print(f"Starting from Frame: {slice_value[:n]} Frames")
# print("-"*80)
# print(f"Total Entropy: {total_entropy[:n]} J/mol*K")
# print(f"Vibrational Entropy: {vibrational_entropy[:n]} J/mol*K")
# print(f"Translational Entropy: {translational_entropy[:n]} J/mol*K")
# print(f"Rotational Entropy: {rotational_entropy[:n]} J/mol*K")

# print("-"*80)
# print(f"Average total entropy from {simulation_time[n]} picoseconds onwards: {np.mean(total_entropy[:n]):.2f} J/mol*K")
# print(f"StDev total entropy from last {simulation_time[n]} picoseconds onwards: {np.std(total_entropy[:n]):.2f} J/mol*K")
# print("-"*80)
# print(f"Average vibrational_entropy from {simulation_time[n]} picoseconds onwards: {np.mean(vibrational_entropy[:n]):.2f} J/mol*K")
# print(f"StDev vibrational_entropy from last {simulation_time[n]} picoseconds onwards: {np.std(vibrational_entropy[:n]):.2f} J/mol*K")
# print("-"*80)
# print(f"Average translational_entropy from {simulation_time[n]} picoseconds onwards: {np.mean(translational_entropy[:n]):.2f} J/mol*K")
# print(f"StDev translational_entropy from last {simulation_time[n]} picoseconds onwards: {np.std(translational_entropy[:n]):.2f} J/mol*K")
# print("-"*80)
# print(f"Average rotational_entropy from {simulation_time[n]} picoseconds onwards: {np.mean(rotational_entropy[:n]):.2f} J/mol*K")
# print(f"StDev rotational_entropy from last {simulation_time[n]} picoseconds onwards: {np.std(translational_entropy[:n]):.2f} J/mol*K")
# print("-"*80)