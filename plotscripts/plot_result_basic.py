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
# parser.add_argument('reference',
#                     type=str,
#                     help='the file that has the correct ice thickness')
args = parser.parse_args()

secInMonth = 60 * 60 * 24 * 30


def get_extend(x, y):
    """Read extend from x and y variables and return extend to be used with cartopy"""
    return [x[0], x[-1], y[0], y[-1]]


# the one used in the model
crs = ccrs.NorthPolarStereo(-45, 70)
extent = (-6240000, 6240000, -6240000, 6240000)

vminTemp = -10
vmaxTemp = 10

vminPrec = 0
vmaxPrec = 2000

# fig, axes = plt.subplots(1, 4, subplot_kw={'projection': crs}, figsize=(12, 4))
# axThkObs = axes[0]
# axThk = axes[1]
# axDiff1 = axes[2]
# axDiffPerc = axes[3]
fig, axes = plt.subplots(2, 2, subplot_kw={'projection': crs}, figsize=(8, 8))
axThkObs = axes[0, 0]
axThk = axes[0, 1]
axDiff1 = axes[1, 0]
axDiffPerc = axes[1, 1]
fig.suptitle(args.modelfile.split('/')[-1], fontsize=16)

data = Dataset(args.modelfile, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]
thk = data.variables['thk'][:]
# model_timebnds = data.variables['time_bounds'][:]
#
#
netcdfExtend = get_extend(x, y)

# # print(data.variables['air_temp'].units)
# if data.variables['air_temp_snapshot'].units == 'Kelvin':
#     modeltemp = modeltemp - 273
data.close()


#### original ice thickness
# data = Dataset(args.reference, mode='r')
# thk_reference = data.variables['thk'][:]
# data.close()


cmap = cm.get_cmap('GnBu', 21)  # 11 discrete colors
cmap = cm.get_cmap('RdYlBu_r', 21)  # 11 discrete colors
cmap.set_under(color='white')

cmap_diff = cm.get_cmap('RdBu_r', 21)  # 11 discrete colors

# title = args.modelfile.split('/')[-1]

thk_last = thk[-1, :, :]

thk_first = thk[0, :, :]
# thk_first = thk_reference

print("resultfile:")
print(thk_last.shape)
print("reference file:")
print(thk_first.shape)

thk_diff = thk_last - thk_first
thk_diffperc = thk_diff / thk_first

RMSE = np.sqrt(np.mean(thk_diff**2))
print("RMSE:")
print(RMSE)

axThkObs.coastlines(resolution='110m')
axThkObs.set_extent(netcdfExtend, crs=crs)
# axThk.set_extent(extent, crs=crs)
imgThkObs = axThkObs.imshow(thk_first,
                            transform=crs,
                            extent=netcdfExtend,
                            cmap=cmap,
                            origin='lower',
                            vmin=10,
                            vmax=3500)
cbThkObs = plt.colorbar(imgThkObs, ax=axThkObs, shrink=0.8)
cbThkObs.set_label('Observed Ice Thickness (m)')

axThk.coastlines(resolution='110m')
axThk.set_extent(netcdfExtend, crs=crs)
# axThk.set_extent(extent, crs=crs)
imgThk = axThk.imshow(thk_last,
                      transform=crs,
                      extent=netcdfExtend,
                      cmap=cmap,
                      origin='lower',
                      vmin=10,
                      vmax=3500)
cbThk = plt.colorbar(imgThk, ax=axThk, shrink=0.8)
cbThk.set_label('Model Ice Thickness (m)')

axDiff1.coastlines(resolution='110m')
axDiff1.set_extent(netcdfExtend, crs=crs)
imgDiff = axDiff1.imshow(thk_diff,
                         transform=crs,
                         cmap=cmap_diff,
                         extent=netcdfExtend,
                         origin='lower',
                         vmin=-250,
                         vmax=250)
cbDiff = plt.colorbar(imgDiff, ax=axDiff1, shrink=0.8)
cbDiff.set_label('Thickness difference (m) (model - observation)')

axDiffPerc.coastlines(resolution='110m')
axDiffPerc.set_extent(netcdfExtend, crs=crs)
imgDiffPerc = axDiffPerc.imshow(thk_diffperc,
                                transform=crs,
                                extent=netcdfExtend,
                                cmap=cmap_diff,
                                origin='lower',
                                vmin=-1,
                                vmax=1)
cbDiffPerc = plt.colorbar(imgDiffPerc, ax=axDiffPerc, shrink=0.8)
cbDiffPerc.set_label('Thickness difference (normalized)')

# axThk.set_title(title)

# ax.gridlines()
print(args.modelfile + "result" + ".png")
plt.savefig(args.modelfile + "result" + ".png", dpi=300)
