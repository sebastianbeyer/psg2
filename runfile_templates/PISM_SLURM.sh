#!/usr/bin/env bash
## PISM runscript created by psg on {{ timestamp  }}
## git revision: {{ psg_revision }}
##
## {{ exp_name }}
##

#SBATCH --partition=clx
#SBATCH --ntasks=40
#SBATCH --tasks-per-node=40
#SBATCH --time=12:00:00
#SBATCH --mail-user=sbeyer@marum.de
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output=pism.%j


srun --mpi=pmix pismr \

