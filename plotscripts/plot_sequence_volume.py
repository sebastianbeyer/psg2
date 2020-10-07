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
args = parser.parse_args()

directory = os.fsencode(args.directory)
fig, (ax) = plt.subplots(1, 1, sharey=False, figsize=(6, 6))

fileList = os.listdir(directory)
fileList = natsort.natsorted(fileList, alg=natsort.ns.IGNORECASE)
for file in fileList:
    filename = os.fsdecode(file)
    if filename.startswith("ts_") and filename.endswith(".nc"):
        current_file = os.path.join(args.directory, filename)
        print(current_file)
        data = Dataset(current_file, mode='r')
        time = data.variables['time'][:]
        volume = data.variables['ice_volume'][:]
        data.close()
        ax.plot(time, volume, label=str(filename))
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

# ax.axhline(y=2.93)  # this is from RACMO2 maybe?
# ax.set_ylabel('Ice volume (Mio km^2)')
ax.legend()
plt.savefig(args.directory + "/volume_sequence" + ".png", dpi=300)
