#!/usr/bin/env bash
## PISM runscript created by psg on {{ timestamp  }}
## git revision: {{ psg_revision }}
##
## {{ exp_name }}
##

####

mpiexec -n {{ n_procs }} --use-hwthread-cpus pismr \

