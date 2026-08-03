import warnings
warnings.filterwarnings("ignore")
from mace.cli.run_train import main as mace_run_train_main
import sys
import logging

# import torch
# print("CUDA available:", torch.cuda.is_available())
# print("CUDA version (PyTorch):", torch.version.cuda)
# print("Device name:", torch.cuda.get_device_name(0))

# import cuequivariance as cue
# import cuequivariance_torch
# print("cuequivariance available:", cue is not None)

def train_mace(config_file_path):
    logging.getLogger().handlers.clear()
    sys.argv = ["program", "--config", config_file_path]
    mace_run_train_main()

train_mace("metal_training.yml")