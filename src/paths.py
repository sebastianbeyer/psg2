import os
import sys

# get location of this stuff and add the paths, so no install is necessary
psg_file = os.path.realpath(os.path.expanduser(__file__))
psg_prefix = os.path.dirname(os.path.dirname(psg_file))

# print(psg_prefix)
psg_src_path = os.path.join(psg_prefix, "src")

setups_path = os.path.join(psg_prefix, "setups")
templates_path = os.path.join(psg_prefix, "runfile_templates")

exp_envs_path = os.path.join(psg_prefix, 'experiments')
pism_config_path = os.path.join(psg_prefix, 'pism_config_file')
