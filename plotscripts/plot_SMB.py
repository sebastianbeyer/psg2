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


def get_extend(x, y):
    """Read extend from x and y variables and return extend to be used with cartopy"""
    return [x[0], x[-1], y[0], y[-1]]


data = Dataset(args.modelfile, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]
# thk = data.variables['thk'][:]
# climatic_mass_balance,effective_precipitation,effective_air_temp,air_temp_snapshot,surface_accumulation_flux,surface_melt_flux,surface_runoff_flux,surface_layer_thickness
cmb = data.variables['climatic_mass_balance'][:]
air_temp = data.variables['air_temp_snapshot'][:]
precip = data.variables['effective_precipitation'][:]
air_temp_e = data.variables['effective_air_temp'][:]
accum = data.variables['surface_accumulation_flux'][:]
melt = data.variables['surface_melt_flux'][:]
runoff = data.variables['surface_runoff_flux'][:]
layer = data.variables['surface_layer_thickness'][:]
usurf = data.variables['surface_layer_thickness'][:]

air_temp = air_temp_e
air_temp = air_temp - 273.15

# # print(data.variables['air_temp'].units)
# if data.variables['air_temp_snapshot'].units == 'Kelvin':
#     modeltemp = modeltemp - 273
data.close()

usurf = usurf[-1, :, :]

netcdfExtend = get_extend(x, y)
extent = netcdfExtend

cmap = cm.get_cmap('GnBu', 21)    # 11 discrete colors
cmap = cm.get_cmap('RdBu', 21)    # 11 discrete colors
cmap_temp = cm.get_cmap('RdBu_r', 21)    # 11 discrete colors
# cmap_diff = cm.get_cmap('RdBu', 21)    # 11 discrete colors
#

# custom colormap as in the paper
bounds = [-6400, -3200, -1600, -800, -400, -200, -100, -50, -25, -5, 0,
          5, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400]

norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
cmap = cm.get_cmap('RdBu')


title = args.modelfile.split('/')[-1]

fig, axes = plt.subplots(1,
                         5,
                         subplot_kw={'projection': crs},
                         figsize=(16, 8))
# print(axes)


CMBmean = np.mean(cmb, axis=0)
air_temp_mean = np.mean(air_temp, axis=0)
precip_mean = np.mean(precip, axis=0)
accum_mean = np.mean(accum, axis=0)
melt_mean = np.mean(melt, axis=0)

CMBmasked = np.ma.masked_equal(CMBmean, 0)
CMBsinglemean = np.mean(CMBmasked)

print("mean smb")
print(CMBsinglemean)

##############################
shrink = 0.9

axCMB = axes[0]
axCMB.coastlines(resolution='110m')
axCMB.set_extent(extent, crs=crs)
imgCMB = axCMB.imshow(CMBmean,
                      transform=crs,
                      extent=netcdfExtend,
                      cmap=cmap,
                      norm=norm,
                      origin='lower',
                      )
cbCMB = plt.colorbar(imgCMB, ax=axCMB, shrink=shrink, orientation="horizontal")
cbCMB.set_label('climatic mass balance')

# axCMB.set_title(title + "\n" + "mean: {:6.0f}".format(CMBsinglemean))
fig.suptitle(title + "\n" + "mean: {:6.0f}".format(CMBsinglemean))
#####################################################

axAir_temp = axes[1]
axAir_temp.coastlines(resolution='110m')
axAir_temp.set_extent(extent, crs=crs)
imgAir_temp = axAir_temp.imshow(air_temp_mean,
                                transform=crs,
                                extent=netcdfExtend,
                                cmap=cmap_temp,
                                vmin=-30,
                                vmax=30,
                                origin='lower',
                                )
cbAir_temp = plt.colorbar(imgAir_temp, ax=axAir_temp,
                          shrink=shrink, orientation="horizontal")
cbAir_temp.set_label('air temperature (K)')


axPrecip = axes[2]
axPrecip.coastlines(resolution='110m')
axPrecip.set_extent(extent, crs=crs)
imgPrecip = axPrecip.imshow(precip_mean,
                            transform=crs,
                            extent=netcdfExtend,
                            cmap=cmap,
                            norm=norm,
                            origin='lower',
                            )
cbPrecip = plt.colorbar(imgPrecip, ax=axPrecip,
                        shrink=shrink, orientation="horizontal")
cbPrecip.set_label('precipitation')

axAccum = axes[3]
axAccum.coastlines(resolution='110m')
axAccum.set_extent(extent, crs=crs)
imgAccum = axAccum.imshow(accum_mean,
                          transform=crs,
                          extent=netcdfExtend,
                          cmap=cmap,
                          norm=norm,
                          origin='lower',
                          )
cbAccum = plt.colorbar(imgAccum, ax=axAccum,
                       shrink=shrink, orientation="horizontal")
cbAccum.set_label('accumulation')

axMelt = axes[4]
axMelt.coastlines(resolution='110m')
axMelt.set_extent(extent, crs=crs)
imgMelt = axMelt.imshow(-melt_mean,
                        transform=crs,
                        extent=netcdfExtend,
                        cmap=cmap,
                        norm=norm,
                        origin='lower',
                        )
cbMelt = plt.colorbar(imgMelt, ax=axMelt, shrink=shrink,
                      orientation="horizontal")
cbMelt.set_label('melt')
# ax.gridlines()
plt.tight_layout()
plt.savefig(args.modelfile + "_CMB" + ".png", dpi=300)
