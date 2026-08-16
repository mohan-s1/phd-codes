#!/bin/bash

ml gcc openmpi

export PATH=/project/paolucci/new_software/plumed-2.10.0/bin:$PATH

export PATH=/project/paolucci/new_software/plumed-2.10.0/lib:$PATH

export LD_LIBRARY_PATH=/project/paolucci/new_software/plumed-2.10.0/lib:$LD_LIBRARY_PATH

plumed sum_hills --hills HILLS