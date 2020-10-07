#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.colors as colors
import cmocean.cm as cmo
import numpy as np
from pylab import cm

from netCDF4 import Dataset

parser = argparse.ArgumentParser()
parser.add_argument('modelfile', type=str)
args = parser.parse_args()

secInMonth = 60*60*24*30

# the one used in the model
crs = ccrs.NorthPolarStereo(-45, 70)
extent = (-6240000, 6240000, -6240000, 6240000)

vminTemp = -10
vmaxTemp = 10

vminPrec = 0
vmaxPrec = 2000



data = Dataset(args.modelfile, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]
# thk = data.variables['thk'][:]
cmb = data.variables['climatic_mass_balance'][:]
# model_timebnds = data.variables['time_bounds'][:]

# # print(data.variables['air_temp'].units)
# if data.variables['air_temp_snapshot'].units == 'Kelvin':
#     modeltemp = modeltemp - 273
data.close()


cmap = cm.get_cmap('GnBu', 21)    # 11 discrete colors
cmap = cm.get_cmap('RdBu', 21)    # 11 discrete colors
# cmap_diff = cm.get_cmap('RdBu', 21)    # 11 discrete colors
#

## custom colormap as in the paper
bounds = [-6400, -3200, -1600, -800, -400, -200, -100, -50, -25, -5, 0,
          5, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400]

norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
cmap = cm.get_cmap('RdBu')


title = args.modelfile.split('/')[-1]

fig, axes = plt.subplots(1,
                         1,
                         subplot_kw={'projection': crs},
                         figsize=(4, 4))
print(axes)

axCMB = axes

CMBmean = np.mean(cmb, axis=0)


axCMB.coastlines(resolution='110m')
axCMB.set_extent(extent, crs=crs)
imgCMB = axCMB.imshow(CMBmean,
                        transform=crs,
                        extent=[-6240000, 6240000, -6240000, 6240000],
                        cmap=cmap,
                        norm=norm,
                        origin='lower',
                        )
cbCMB = plt.colorbar(imgCMB, ax=axCMB, shrink=0.8)
cbCMB.set_label('climatic mass balance')

axCMB.set_title(title)

# ax.gridlines()
plt.savefig(args.modelfile + "_CMB" + ".png", dpi=300)
