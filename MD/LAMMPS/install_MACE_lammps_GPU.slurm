#!/bin/bash
#SBATCH --account=paolucci_standard
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a6000:1
#SBATCH --time=0-03:00:00
#SBATCH --output=install_mace_lammps_gpu.out
#SBATCH --error=install_mace_lammps_gpu.err
#SBATCH --mail-type=ALL

module purge 

git clone --branch=mace --depth=1 https://github.com/ACEsuit/lammps lammps_gpu
wget https://download.pytorch.org/libtorch/cu121/libtorch-shared-with-deps-2.2.0%2Bcu121.zip
unzip libtorch-shared-with-deps-2.2.0+cu121.zip
rm libtorch-shared-with-deps-2.2.0+cu121.zip
mv libtorch libtorch-gpu

module load gcc/14.2.0 openmpi/5.0.7 cuda/12.8.0 cudnn/9.8.0-CUDA-12.8.0 cmake/4.1.2 imkl/2025.0.1

echo "CUDA HOME IS LOCATED IN:"
echo $CUDA_HOME

cd lammps_gpu

sed -i 's/cmake_minimum_required(VERSION 3\.[0-9]\+ FATAL_ERROR)/cmake_minimum_required(VERSION 3.10 FATAL_ERROR)/' cmake/Modules/Packages/ML-MACE.cmake

mkdir build-ampere
cd build-ampere
cmake \
    -DCMAKE_PREFIX_PATH=$CUDA_HOME \
    -DCUDAToolkit_ROOT=$CUDA_HOME \
    -DCUDA_TOOLKIT_ROOT_DIR=$CUDA_HOME \
    -DNVTOOLSEXT_LIBRARY=$CUDA_HOME/lib64/libnvToolsExt.so \
    -D CMAKE_BUILD_TYPE=Release \
    -D CMAKE_INSTALL_PREFIX=$(pwd) \
    -D CMAKE_CXX_STANDARD=17 \
    -D CMAKE_CXX_STANDARD_REQUIRED=ON \
    -D BUILD_MPI=ON \
    -D BUILD_SHARED_LIBS=ON \
    -D PKG_KOKKOS=ON \
    -D Kokkos_ENABLE_CUDA=ON \
    -D CMAKE_CXX_COMPILER=$(pwd)/../lib/kokkos/bin/nvcc_wrapper \
    -D Kokkos_ARCH_AMDAVX=ON \
    -D Kokkos_ARCH_AMPERE100=ON \
    -D CMAKE_PREFIX_PATH=$(pwd)/../../libtorch-gpu \
    -D PKG_ML-MACE=ON \
    ../cmake
make -j 20
make install