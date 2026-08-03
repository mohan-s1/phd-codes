#!/bin/bash

module purge

module load uv

cd

uv venv --python 3.12 mace_env

source mace_env/bin/activate

uv pip install mace-torch

git clone https://github.com/ChengUCB/les.git

cd les

uv pip install -e . 