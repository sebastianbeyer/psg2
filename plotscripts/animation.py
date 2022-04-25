#!/usr/bin/env python3

from matplotlib import animation
import subprocess
import sys
import os
import scipy.ndimage
import scipy as sp
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as mticker
import argparse
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.colors as colors
import cmocean.cm as cmo
import numpy as np
from pylab import cm

from netCDF4 import Dataset
import matplotlib


parser = argparse.ArgumentParser()
parser.add_argument('icemodel', type=str)
parser.add_argument('--variable', type=str, default="thk",
                    choices=["thk", "vel", "temppabase"])
parser.add_argument('--timestep', type=int, default=-1,)
args = parser.parse_args()

secInMonth = 60 * 60 * 24 * 30

params = {
    'text.latex.preamble': ['\\usepackage{gensymb}'],
    'image.origin': 'lower',
    'image.interpolation': 'nearest',
    'image.cmap': 'gray',
    'axes.grid': False,
    'savefig.dpi': 150,  # to adjust notebook inline plot size
    'axes.labelsize': 8,  # fontsize for x and y labels (was 10)
    'axes.titlesize': 8,
    'font.size': 8,  # was 10
    'legend.fontsize': 6,  # was 10
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    # 'text.usetex': True,
    'figure.figsize': [3.39, 2.10],
    'font.family': 'serif',
}
matplotlib.rcParams.update(params)


def makeGreenlandColormap(velodata):
    d = np.log(np.clip(velodata, 1, 3000))
    data_scale = (255 * (d - np.amin(d)) / np.ptp(d)).astype(np.uint8)

    # Construct an RGB table using a log scale between 1 and 3000 m/year.
    vel = np.exp(np.linspace(np.log(1), np.log(3000), num=256))
    hue = np.arange(256) / 255.0
    sat = np.clip(1. / 3 + vel / 187.5, 0, 1)
    value = np.zeros(256) + 0.8
    hsv = np.stack((hue, sat, value), axis=1)
    rgb = colors.hsv_to_rgb(hsv)
    # Be sure the first color (the background) is white
    rgb[0, :] = 1
    cmap = colors.ListedColormap(rgb, name='velocity')

    tickval = [1, 10, 100, 1000, 3000]
    t = np.log(tickval)
    ticks = 255*(t - t[0])/(t[-1] - t[0])
    # cb = plt.colorbar(fig, ticks=255*(t - t[0])/(t[-1] - t[0]), shrink=0.5)

    return data_scale, cmap, ticks, tickval


def hillshade(array, azimuth, angle_altitude):
    azimuth = 360.0 - azimuth

    x, y = np.gradient(array)
    slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
    aspect = np.arctan2(-x, y)
    azimuthrad = azimuth*np.pi/180.
    altituderad = angle_altitude*np.pi/180.

    shaded = np.sin(altituderad)*np.sin(slope) + np.cos(altituderad) * \
        np.cos(slope)*np.cos((azimuthrad - np.pi/2.) - aspect)

    return 255*(shaded + 1)/2


def get_extend(x, y):
    """Read extend from x and y variables and return extend to be used with cartopy"""
    return [x[0], x[-1], y[0], y[-1]]


# the one used in the model
crs = ccrs.NorthPolarStereo(-45, 70)
# crs = ccrs.NorthPolarStereo(-39, 71)


data = Dataset(args.icemodel, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]
# usurf = data.variables['usurf'][:]
thk = data.variables['thk'][:]
vel = data.variables['velsurf_mag'][:]
temppabase = data.variables['temppabase'][:]
mask = data.variables['mask'][:]
time = data.variables['time'][:]

data.close()

X, Y = np.meshgrid(x, y)
thk_last = thk[args.timestep, :, :]
# usurf_last = usurf[-1, :, :]
usurf_last = thk_last
vel_last = vel[args.timestep, :, :]
temppabase_last = temppabase[args.timestep, :, :]
mask_last = mask[args.timestep, :, :] != 2

temppabase_last[mask_last] = np.nan

time_selected = time[args.timestep]
time_sel_ka = time_selected / 60 / 60 / 24 / 365 / 1000
time_ka = time / 60 / 60 / 24 / 365 / 1000

print("timestep: {} ka".format(time_sel_ka))


# smooth topo
sigma = [3, 3]
surf_smooth = sp.ndimage.filters.gaussian_filter(
    usurf_last, sigma, mode='constant')


# hillshade = hillshade(surf, 225, 75)
hillshade_single = hillshade(surf_smooth, 225, 75)

hillshade1 = hillshade(surf_smooth, 270, 55)
hillshade2 = hillshade(surf_smooth, 15, 60)
hillshade3 = hillshade(surf_smooth, 350, 70)

hillshade_multi = hillshade1 * 0.2 + hillshade2 * 0.3 + hillshade3 * 0.5

hillshade = hillshade_multi

netcdfExtend = get_extend(x, y)
extent = [-5000000, 5000000, -5000000, 5000000]

cmap = cm.get_cmap('GnBu', 21)  # 11 discrete colors
cmap = cm.get_cmap('RdYlBu_r', 21)  # 11 discrete colors
cmap = cm.get_cmap('YlOrBr', 21)  # 11 discrete colors
cmap.set_under(color='white')

cmap_temp = cmo.thermal

cmap_diff = cm.get_cmap('RdBu_r', 21)  # 11 discrete colors

vel_surf_scaled, cmap_GRN, ticks, tickval = makeGreenlandColormap(vel_last)


fig, axes = plt.subplots(1, 1, subplot_kw={'projection': crs}, figsize=(6, 6))


axes.set_extent(extent, crs=crs)
axes.coastlines(resolution='110m', color='gray', alpha=0.3)

if args.variable == "thk":
    imgThkObs = axes.imshow(thk_last,
                            transform=crs,
                            extent=netcdfExtend,
                            cmap=cmap,
                            origin='lower',
                            vmin=000,
                            vmax=4000)
    cbThkObs = plt.colorbar(imgThkObs, ax=axes, shrink=0.7, pad=0.08)
    cbThkObs.set_label('Ice Thickness (m)')


if args.variable == "vel":
    imgThkObs = axes.imshow(vel_surf_scaled,
                            transform=crs,
                            extent=netcdfExtend,
                            cmap=cmap_GRN,
                            origin='lower',
                            )
    cbThkObs = plt.colorbar(imgThkObs, ticks=ticks,
                            ax=axes, shrink=0.7, pad=0.08)
    cbThkObs.ax.set_yticklabels(tickval)
    # cb = plt.colorbar(fig, ticks=255*(t - t[0])/(t[-1] - t[0]), shrink=0.5)
    cbThkObs.set_label('Ice Surface Velocity (m/a)')

if args.variable == "temppabase":
    imgThkObs = axes.imshow(temppabase_last,
                            transform=crs,
                            extent=netcdfExtend,
                            cmap=cmap_temp,
                            origin='lower',
                            )
    cbThkObs = plt.colorbar(imgThkObs, ax=axes, shrink=0.7, pad=0.08)
    cbThkObs.set_label('Basal Temperature (C) pressure adjusted')

hillshade = axes.imshow(hillshade,
                        transform=crs,
                        extent=netcdfExtend,
                        cmap="Greys_r",
                        origin='lower',
                        vmin=0,
                        vmax=255,
                        alpha=0.3)

yeartext = plt.text(0.9, 0.95, '0', ha='center',
                    va='center', transform=axes.transAxes)

# marker
#axes.plot(-45, 70, transform=ccrs.PlateCarree(), marker='o', markersize=30 )

# axes.contour(X, Y, icefrac_last, levels=[0.1, ],
#              colors=('white',), linestyles=('-',), linewidths=(1.1,))


# axes.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
#
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, dms=True,
                    x_inline=False, y_inline=False, linestyle='--', linewidth=.5, color='k', alpha=0.3,
                    )

gl.bottom_labels = False
gl.left_labels = False
gl.rotate_labels = False
# gl.xlines = False
gl.ylocator = mticker.FixedLocator([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
# gl.ylocator = mticker.FixedLocator([-90, -80, -70, -60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
# gl.xlocator = mticker.FixedLocator(np.arange(-180, 180, 20))
gl.xlocator = mticker.FixedLocator(np.arange(-180, 180, 45))
gl.ypadding = 15

#
# axes.gridlines(crs=crs, )

# axes.set_xticks([0, 60, 120, 180, 240, 300, 360], crs=ccrs.PlateCarree())
axes.set_xticks([-4000000, -2000000, 0, 2000000, 4000000], )
axes.set_yticks([-4000000, -2000000, 0, 2000000, 4000000], )
# axes.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
# lon_formatter = LongitudeFormatter(zero_direction_label=True)
# lat_formatter = LatitudeFormatter()
# axes.xaxis.set_major_formatter(lon_formatter)
# aes1.yaxis.set_major_formatter(lat_formatter)


def kilometer(x, pos):
    'The two args are the value and tick position'
    return "{:d} km".format(int(x*1e-3))


formatter = FuncFormatter(kilometer)
axes.xaxis.set_major_formatter(formatter)
axes.yaxis.set_major_formatter(formatter)
axes.yaxis.set_tick_params(rotation=90)
# ylabels = axes.yaxis.get_ticklabels()
# print(ylabels)
# axes.set_yticklabels(ylabels, rotation=90, rotation_mode="anchor")
#


def animate(i):
    print(i)

    vel_surf_scaled, cmap_GRN, ticks, tickval = makeGreenlandColormap(
        vel[i, :, :])
    print("done scaling")
    # imgThkObs = axes.imshow(vel_surf_scaled,
    #                         transform=crs,
    #                         extent=netcdfExtend,
    #                         cmap=cmap_GRN,
    #                         origin='lower',
    #                         )
    imgThkObs.set_data(vel_surf_scaled)
    yeartext.set_text("{} ka".format(time_ka[i]))
    # hillshade = axes.imshow(hillshade,
    #                         transform=crs,
    #                         extent=netcdfExtend,
    #                         cmap="Greys_r",
    #                         origin='lower',
    #                         vmin=0,
    #                         vmax=255,
    #                         alpha=0.3)


plt.tight_layout()

# anim = animation.FuncAnimation(fig, animate, blit=False, frames=200)
# anim.save("test.mp4", dpi=100, writer='imagemagick')
#
#
anim = animation.FuncAnimation(fig, animate, blit=False, frames=500)

anim.save("test.mp4", fps=5, extra_args=[
          '-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])

# anim.save("test.mp4", dpi=100, writer='imagemagick')

# plotfile = args.icemodel + "_nice_" + \
#     str(args.variable) + str(args.timestep) + ".png"
# plt.savefig(plotfile, dpi=300)


#subprocess.call(["xdg-open", plotfile])
