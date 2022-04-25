#!/usr/bin/env python3

from colorama import Style
from colorama import Fore
import argparse
import numpy as np
import os
from netCDF4 import Dataset
from matplotlib import cm

secondsperyear = 60*60*24*365

parser = argparse.ArgumentParser()
parser.add_argument('files', type=str, nargs='+')
args = parser.parse_args()

for file in args.files:
    data = Dataset(file, mode='r')
    conf = data.variables['pism_config']

    # siae = conf["stress_balance.sia.enhancement_factor"]
    siae = conf.getncattr("stress_balance.sia.enhancement_factor")
    ssae = conf.getncattr("stress_balance.ssa.enhancement_factor")
    ppq = conf.getncattr("basal_resistance.pseudo_plastic.q")
    uthresh = conf.getncattr("basal_resistance.pseudo_plastic.u_threshold")
    ttp_pmax = conf.getncattr(
        "basal_yield_stress.mohr_coulomb.topg_to_phi.phi_max")
    ttp_pmin = conf.getncattr(
        "basal_yield_stress.mohr_coulomb.topg_to_phi.phi_min")
    ttp_tmax = conf.getncattr(
        "basal_yield_stress.mohr_coulomb.topg_to_phi.topg_max")
    ttp_tmin = conf.getncattr(
        "basal_yield_stress.mohr_coulomb.topg_to_phi.topg_min")

    print(f"siae: {Fore.GREEN}{siae} {Style.RESET_ALL}")
    print(f"ssae: {Fore.GREEN}{ssae} {Style.RESET_ALL}")
    print(f"ppq: {Fore.GREEN}{ppq} {Style.RESET_ALL}")
    print(f"utresh: {Fore.GREEN}{uthresh} {Style.RESET_ALL}")

    print(
        f"topg_to_phi: {Fore.GREEN}{ttp_pmin}/{ttp_pmax}/{ttp_tmin}/{ttp_tmax} {Style.RESET_ALL}")

# print(conf)
data.close()
