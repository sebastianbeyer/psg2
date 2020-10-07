#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import cmocean.cm as cmo
import numpy as np
import os
import natsort
from netCDF4 import Dataset

parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str)
parser.add_argument(
    'variable',
    type=str,
    help="PISM config name, e.g. stress_balance.sia.enhancement_factor")
parser.add_argument('--mask',
                    help="mask file for greenland",
                    default='none',
                    type=str)
parser.add_argument('--velo',
                    help="observed velocity field",
                    default='none',
                    type=str)
args = parser.parse_args()

directory = os.fsencode(args.directory)

fig, (ax) = plt.subplots(1, 1, sharey=False, figsize=(6, 6))

if args.velo != "none":
    data = Dataset(args.velo, mode='r')
    vel_obs = data.variables['vv'][:]
    data.close()

fileList = os.listdir(directory)
fileList = natsort.natsorted(fileList, alg=natsort.ns.IGNORECASE)
for file in fileList:
    filename = os.fsdecode(file)
    if filename.startswith("ex_") and filename.endswith(".nc"):
        current_file = os.path.join(args.directory, filename)
        print(current_file)
        data = Dataset(current_file, mode='r')
        x = data.variables['x'][:]
        y = data.variables['y'][:]
        thk = data.variables['thk'][:]
        vel = data.variables['velsurf_mag'][:]
        maskPISM = data.variables['mask'][:]
        conf = data.variables['pism_config']
        # varValue = conf.getncattr('stress_balance.sia.enhancement_factor')
        varValue = conf.getncattr(args.variable)
        data.close()
        dx = x[1] - x[0]
        nTimesteps = thk.shape[0]

        target_thk = thk[0, :, :]
        model_thk = thk[-1, :, :]

        vel_model = vel[-1, :, :]

        icemass = []
        iceVolume = []
        for i in range(nTimesteps):
            icemass.append(np.sum(thk[i, :, :]) * dx * dx * 910 / 1e12)
            iceVolume.append(np.sum(thk[i, :, :]) * dx * dx)

        iceVolume = np.array(iceVolume) / 1e15
        ax.plot(iceVolume, label=str(varValue))
        # ax.plot(target_thk.flatten(),
        #         model_thk.flatten(),
        #         'o',
        #         alpha=0.5,
        #         label=str(varValue))

        # ax.plot(vel_obs.flatten(),
        #         vel_model.flatten(),
        #         'o',
        #         alpha=0.5,
        #         label=str(varValue))
# ax.set_xlim([50, 600])
# ax.set_ylim([50, 600])

ax.axhline(y=2.93)  # this is from RACMO2 maybe?
# ax.set_ylabel('Ice volume (Mio km^2)')
ax.legend()
plt.savefig(args.directory + "/mass_over_time" + ".png", dpi=300)
