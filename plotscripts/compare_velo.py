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
parser.add_argument('veloreference',
                    type=str,
                    help="What to compare to (thruth)")
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
netcdfExtend = get_extend(x, y)
data.close()

data = Dataset(args.veloreference, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]
vel_reference = data.variables['vel_mag'][:]
data.close()

# look only at last timestep
vel_surf = vel_surf[-1, :, :]

difference = vel_surf - vel_reference

RMSE = np.sqrt(np.mean(difference**2))
print("RMSE:")
print(RMSE)

fig, axes = plt.subplots(1, 4, subplot_kw={'projection': crs}, figsize=(12, 4))

cmap = cm.get_cmap('GnBu', 21)  # 11 discrete colors
cmap_diff = cm.get_cmap('RdBu_r', 21)  # 11 discrete colors

vel_surf_scaled, cmap_GRN = makeGreenlandColormap(vel_surf)
vel_surf_scaled_reference, cmap_GRN = makeGreenlandColormap(vel_reference)
tickval = [1, 10, 100, 1000, 3000]
t = np.log(tickval)

title = args.modelfile.split('/')[-1]

axVel = axes[1]
axVelRef = axes[0]
axDiff = axes[2]
axScatter = axes[3]

axVel.coastlines(resolution='110m')
axVel.set_extent(netcdfExtend, crs=crs)
imgVel = axVel.imshow(
    vel_surf_scaled,
    transform=crs,
    extent=netcdfExtend,
    cmap=cmap_GRN,
    origin='lower',
)

cbVel = plt.colorbar(imgVel,
                     ax=axVel,
                     ticks=255 * (t - t[0]) / (t[-1] - t[0]),
                     shrink=0.8)
cbVel.ax.set_yticklabels(tickval)
cbVel.set_label('Model Surface Velocity (m/yr)')

axVelRef.coastlines(resolution='110m')
axVelRef.set_extent(netcdfExtend, crs=crs)
imgVelRef = axVelRef.imshow(
    vel_surf_scaled_reference,
    transform=crs,
    extent=netcdfExtend,
    cmap=cmap_GRN,
    origin='lower',
)
cbVelRef = plt.colorbar(imgVelRef,
                        ax=axVelRef,
                        ticks=255 * (t - t[0]) / (t[-1] - t[0]),
                        shrink=0.8)
cbVelRef.ax.set_yticklabels(tickval)
cbVelRef.set_label('Observed Surface Velocity(m/yr)')

axDiff.coastlines(resolution='110m')
axDiff.set_extent(netcdfExtend, crs=crs)
imgDiff = axDiff.imshow(difference,
                        transform=crs,
                        extent=netcdfExtend,
                        cmap=cmap_diff,
                        origin='lower',
                        vmin=-250,
                        vmax=250)
cbDiff = plt.colorbar(imgDiff, ax=axDiff, shrink=0.8)
cbDiff.set_label('Difference (m/yr) RMSE: {:4.0f}'.format(RMSE))

axVel.set_title(title)
# axDiff.set_title("RMSE: {:4.0f} m/yr".format(RMSE))

# ax.gridlines()

axScatter.scatter(vel_surf.flatten(), vel_reference.flatten())



print(args.modelfile + "_velodiff" + ".png")
plt.savefig(args.modelfile + "_velodiff" + ".png", dpi=300)
