#!/bin/bash

module purge

module load uv

cd

uv venv --python 3.12 uv_mlp

source uv_mlp/bin/activate

cd uv_mlp

uv pip install mace-torch orb-models ase torch-sim-atomistic torch numpy

git clone https://github.com/ChengUCB/les.git

cd les

uv pip install -e . 