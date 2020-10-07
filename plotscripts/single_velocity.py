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

secInMonth = 60 * 60 * 24 * 30

######## colormap Greenland Velo ########


def makeGreenlandColormap(velodata):
    d = np.log(np.clip(velodata, 1, 3000))
    data_scale = (255 * (d - np.amin(d)) / np.ptp(d)).astype(np.uint8)

    # Construct an RGB table using a log scale between 1 and 3000 m/year.
    vel = np.exp(np.linspace(np.log(1), np.log(3000), num=256))
    hue = np.arange(256) / 255.0
    sat = np.clip(1. / 3 + vel / 187.5, 0, 1)
    value = np.zeros(256) + 0.75
    hsv = np.stack((hue, sat, value), axis=1)
    rgb = colors.hsv_to_rgb(hsv)
    # Be sure the first color (the background) is white
    rgb[0, :] = 1
    cmap = colors.ListedColormap(rgb, name='velocity')
    return data_scale, cmap


############################################


def get_extend(x, y):
    """Read extend from x and y variables and return extend to be used with cartopy"""
    return [x[0], x[-1], y[0], y[-1]]


# the one used in the model
crs = ccrs.NorthPolarStereo(-45, 70)

data = Dataset(args.modelfile, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]
thk = data.variables['thk'][:]
vel_surf = data.variables['velsurf_mag'][:]
vel_base = data.variables['velbase_mag'][:]
netcdfExtend = get_extend(x, y)
data.close()

# look only at last timestep
vel_surf = vel_surf[-1, :, :]
vel_base = vel_base[-1, :, :]

sliding = vel_base / vel_surf * 100

fig, axes = plt.subplots(1, 3, subplot_kw={'projection': crs}, figsize=(12, 4))

cmap = cm.get_cmap('GnBu', 21)  # 11 discrete colors
cmap_diff = cm.get_cmap('RdBu', 21)  # 11 discrete colors
cmap_slide = cm.get_cmap('RdBu_r', 21)  # 11 discrete colors

vel_surf_scaled, cmap_GRN = makeGreenlandColormap(vel_surf)
vel_base_scaled, cmap_GRN = makeGreenlandColormap(vel_base)
tickval = [1, 10, 100, 1000, 3000]
t = np.log(tickval)

title = args.modelfile.split('/')[-1]

axVel = axes[0]
axVelBase = axes[1]
axSlide = axes[2]

axVel.coastlines(resolution='110m')
axVel.set_extent(netcdfExtend, crs=crs)
imgVel = axVel.imshow(
    vel_surf_scaled,
    transform=crs,
    extent=netcdfExtend,
    cmap=cmap_GRN,
    origin='lower',
)
cbVel = plt.colorbar(imgVel, ax=axVel, ticks=255*(t - t[0])/(t[-1] - t[0]), shrink=0.8)
cbVel.ax.set_yticklabels(tickval)
cbVel.set_label('Ice Surface Velocity (m/yr)')

axVelBase.coastlines(resolution='110m')
axVelBase.set_extent(netcdfExtend, crs=crs)
imgVelBase = axVelBase.imshow(vel_base_scaled,
                              transform=crs,
                              extent=netcdfExtend,
                              cmap=cmap_GRN,
                              origin='lower',)
cbVelBase = plt.colorbar(imgVelBase, ax=axVelBase, ticks=255*(t - t[0])/(t[-1] - t[0]), shrink=0.8)
cbVelBase.ax.set_yticklabels(tickval)
cbVelBase.set_label('Ice Basal Velocity(m/yr)')

axSlide.coastlines(resolution='110m')
axSlide.set_extent(netcdfExtend, crs=crs)
imgSlide = axSlide.imshow(sliding,
                          transform=crs,
                          extent=netcdfExtend,
                          cmap=cmap_slide,
                          origin='lower',
                          vmin=0,
                          vmax=100)
cbSlide = plt.colorbar(imgSlide, ax=axSlide, shrink=0.8)
cbSlide.set_label('Ice Velocity (m/yr)')

axVelBase.set_title(title)

# ax.gridlines()
print(args.modelfile + "_velocity" + ".png")
plt.savefig(args.modelfile + "_velocity" + ".png", dpi=300)
