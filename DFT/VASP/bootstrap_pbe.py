from ase import Atoms, Atom
from ase.io import read
from ase.calculators.vasp.vasp2 import Vasp2
import os
import re
from shutil import copyfile

cwd = os.getcwd()

bootstrap = {'ediff': [1e-4, 1e-6],
             'ediffg': [-0.05, -0.03]}


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

struc = read(matching_files[0]) # matching_files is technically a list, so we take the first element from it 

for i in range(2):
    vasp_directory = str(bootstrap['ediff'][i]) + '_' + str(bootstrap['ediffg'][i])
    if i != 0:
        previous_vasp_directory = str(bootstrap['ediff'][i - 1]) + '_' + str(bootstrap['ediffg'][i - 1])
        if not os.path.exists(cwd + '/' + vasp_directory):
            os.mkdir(cwd + '/' + vasp_directory)
        copyfile(cwd + '/' + previous_vasp_directory + '/WAVECAR', cwd + '/' + vasp_directory + '/WAVECAR')
        copyfile(cwd + '/' + previous_vasp_directory + '/CHGCAR', cwd + '/' + vasp_directory + '/CHGCAR')
        copyfile(cwd + '/' + previous_vasp_directory + '/CONTCAR', cwd + '/' + vasp_directory + '/POSCAR')

    
    calc = Vasp2(xc = 'PBE', 
                directory = vasp_directory,
                encut = 400,
                ediff = bootstrap['ediff'][i],
                ediffg = bootstrap['ediffg'][i],
                algo = 'Fast',
                ibrion = 2,
                ispin = 2, 
                sigma = 0.03,
                nsw = 500, # ionic steps for geometry opt.
                prec = 'accurate',
                ismear = 0, # 0: insulator 
                lscalapack = False,
                lwave = False, # don't write WAVECAR
                ivdw = 12, # 12: include D3(BJ) dispersion corrections
				lreal='Auto') # may additionally have to set NELECT and NUPDOWN 
    struc.set_calculator(calc)
    print(struc.get_potential_energy())