#!/usr/bin/env bash
## PISM runscript created by psg on {{ timestamp  }}
## git revision: {{ psg_revision }}
##
## {{ exp_name }}
##

#SBATCH --partition=standard96:test
#SBATCH --nodes=1
#SBATCH --tasks-per-node=96
#SBATCH --time=1:00:00
#SBATCH --mail-user=sbeyer@marum.de
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output={{ exp_name }}.%j


spack load pism/ndfqrej # intel version of pism (no parallel netcdf yet...)

srun pismr \

