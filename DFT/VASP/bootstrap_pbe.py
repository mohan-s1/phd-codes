from ase.io import read
from ase.calculators.vasp.vasp2 import Vasp2
import os
from pathlib import Path
from shutil import copy2
import re

cwd = os.getcwd()

def find_poscar_cif_files():
    """
    Finds any file in current working directory that contains "POSCAR" anywhere or ends as `.cif`

    Returns:
        list: path(s) to POSCAR or .cif file 
    """
    # Define the regex pattern to match any filename containing 'POSCAR' anywhere or ending with '.cif'
    pattern = re.compile(r"POSCAR|\.cif$", re.IGNORECASE)
    matching_files = []
    
    # Loop through the current directory's files
    for file_name in os.listdir('.'):
        if pattern.search(file_name):
            matching_files.append(file_name)
    
    return matching_files

# Call the function 
matching_files = find_poscar_cif_files()

structure_path = matching_files[0] # matching_files is technically a list, so we take the first element from it 

def perform_bootstrap(struc_path:str, files_to_copy:dict, bootstrap:dict):

    struc = read(struc_path)
    
    for i in range(len(bootstrap["ediff"])):
        vasp_directory = f"{struc_path}_ediff{bootstrap['ediff'][i]:.0e}_ediffg{bootstrap['ediffg'][i]:.2f}"
        
        os.makedirs(vasp_directory, exist_ok=True)
        
        if i > 0:
            previous_vasp_directory = f"{struc_path}_ediff{bootstrap['ediff'][i-1]:.0e}_ediffg{bootstrap['ediffg'][i-1]:.2f}"
            src = Path(cwd) / previous_vasp_directory
            dst = Path(cwd) / vasp_directory

            for src_name, dst_name in files_to_copy.items():
                copy2(src / src_name, dst / dst_name)
        
        calc = Vasp2(xc = 'PBE',
                    directory = vasp_directory,
                    encut = 400,
                    ediff = bootstrap['ediff'][i],
                    ediffg = bootstrap['ediffg'][i],
                    algo = 'Fast',
                    ibrion = 2, # numerical method used
                    ispin = 2, # spin polarized calculation
                    sigma = 0.03, # coupled with ISMEAR; depends on electronic properties of material
                    nsw = 500, # ionic steps for geometry opt.
                    prec = 'accurate',
                    ismear = 0, # 0: insulator 
                    ncore = 8, # says how to distribute calculations on hardware; pretty empirical 
                    lscalapack = False, # diable ScaLAPACK when running on Afton https://www.rc.virginia.edu/userinfo/hpc/software/vasp/
                    ivdw = 12, # include D3(BJ) dispersion corrections
                    custom = dict(lh5=True), # write WAVECAR, CHARGCAR, CHGCAR in hdf5 format; `custom` key to pass in arguments not supported by ASE
                    lreal='Auto') # let VASP choose b/t real and reciprocal space if you're lazy
        struc.set_calculator(calc)
        print(f"{vasp_directory} potential energy: {struc.get_potential_energy()}")


files_to_copy = { # Source: Destination
                            "WAVECAR": "WAVECAR",
                            "CHGCAR": "CHGCAR",
                            "CONTCAR": "POSCAR",
                            "vaspwave.h5": "vaspwave.h5"}

bootstrap = {'ediff': [1e-4, 1e-6],
             'ediffg': [-0.05, -0.03]}

perform_bootstrap(struc_path=structure_path, files_to_copy=files_to_copy, bootstrap=bootstrap)