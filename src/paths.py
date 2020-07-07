import os
import sys

# get location of this stuff and add the paths, so no install is necessary
psg_file = os.path.realpath(os.path.expanduser(__file__))
psg_prefix = os.path.dirname(os.path.dirname(psg_file))

# print(psg_prefix)
spack_src_path = os.path.join(psg_prefix, "src")

setups_path = os.path.join(psg_prefix, "setups")
templates_path = os.path.join(psg_prefix, "runfile_templates")

gridsfile = os.path.join(setups_path, 'specs', 'grids.yaml')
timesfile = os.path.join(setups_path, 'specs', 'times.yaml')
icedynfile = os.path.join(setups_path, 'specs', 'icedynamics.yaml')
oceansfile = os.path.join(setups_path, 'specs', 'oceans.yaml')
climatesfile = os.path.join(setups_path, 'specs', 'climates.yaml')
expsfile = os.path.join(setups_path, 'experiments', 'base.yaml')

exp_envs_path = os.path.join(psg_prefix, 'experiments')
