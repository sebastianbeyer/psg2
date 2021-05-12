#!/usr/bin/env bash
## PISM runscript created by psg on {{ timestamp  }}
## git revision: {{ psg_revision }}
##
## {{ exp_name }}
##

#SBATCH --partition={{ partition }}
#SBATCH --nodes={{ nnodes }}
#SBATCH --tasks-per-node={{ ntasks }}
#SBATCH --time={{ timelimit }}
#SBATCH --mail-user={{ mail }}
#SBATCH --account={{ account }}
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --output={{ exp_name }}.%j


spack load {{ pism_module }}

srun pismr \

