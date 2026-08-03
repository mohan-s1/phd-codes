from ase.io import read
from ase.calculators.vasp.vasp2 import Vasp2
import os

cwd = os.getcwd()

def perform_singlepoint(struc, frame_label:int):

    bootstrap = {'ediff': [1e-4],
             'ediffg': [-0.05]}
    
    for i in range(len(bootstrap["ediff"])):
        vasp_directory = f"struc_{frame_label}"
        
        os.makedirs(vasp_directory, exist_ok=True)
        
        calc = Vasp2(xc = 'PBE',
                    directory = vasp_directory,
                    encut = 400,
                    ediff = bootstrap['ediff'][i],
                    ediffg = bootstrap['ediffg'][i],
                    algo = 'Fast',
                    ibrion = 2, # numerical method used
                    ispin = 2, # spin polarized calculation
                    sigma = 0.03, # coupled with ISMEAR; depends on electronic properties of material
                    nsw = 0, # ionic steps for geometry opt.
                    prec = 'accurate',
                    ismear = 0, # 0: insulator 
                    ncore = 8, # says how to distribute calculations on hardware; pretty empirical 
                    lscalapack = False, # diable ScaLAPACK when running on Afton https://www.rc.virginia.edu/userinfo/hpc/software/vasp/
                    ivdw = 12, # include D3(BJ) dispersion corrections
                    custom = dict(lh5=True), # write WAVECAR, CHARGCAR, CHGCAR in hdf5 format; `custom` key to pass in arguments not supported by ASE
                    lreal='Auto') # let VASP choose b/t real and reciprocal space if you're lazy
        struc.set_calculator(calc)
        print(f"{vasp_directory} potential energy: {struc.get_potential_energy()}")

all_structures = read("NAME", index = ":")

#indices_to_use = [i for i in range(len(all_structures))] # use all frames

indices_to_use = [] # TODO: specify indices

for index in indices_to_use: # iterate through all structures and perform vasp calc
    specific_structure = all_structures[index]
    perform_singlepoint(struc=specific_structure, frame_label=index)