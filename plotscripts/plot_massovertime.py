#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import cmocean.cm as cmo
import numpy as np

from netCDF4 import Dataset

parser = argparse.ArgumentParser()
parser.add_argument('netcdf', type=str)
parser.add_argument('--mask',
                    help="mask file for greenland",
                    default='none',
                    type=str)
parser.add_argument('--trendstart',
                    help="index of where to start for trend computing",
                    type=int,
                    default=50)
args = parser.parse_args()

ncName = args.netcdf
expName = ncName.split('/')[-1]

data = Dataset(ncName, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]

thk = data.variables['thk'][:]
# vel = data.variables['velsurf_mag'][:]
# acc = data.variables['surface_accumulation_flux'][:]
# run = data.variables['surface_runoff_flux'][:]
# maskPISM = data.variables['mask'][:]
data.close()

print(thk.shape)

if args.mask != "none":
    data = Dataset(args.mask, mode='r')
    mask = data.variables['mask'][:]
    data.close()
    thk = thk * mask
    # acc = acc * mask
    # run = run * mask
    # precEra5 = precEra5 * mask

    surfaceArea = np.sum(mask) * dx**2 * 1e-6  # in km^2
    surfaceArea = surfaceArea / 1e6  # mio square km
    print(surfaceArea, "mio m^2")

# data = Dataset("/home/sbeyer/datasets/era5/era5_clim_20km_wtopo.nc", mode='r')
# # data = Dataset("/home/sbeyer/datasets/era5/era5all_clim_20km_wtopo.nc", mode='r')
# precEra5 = data.variables['precipitation'][:]
# data.close()

dx = x[1] - x[0]
nTimesteps = thk.shape[0]

icemass = []
iceVolume = []

for i in range(nTimesteps):
    icemass.append(np.sum(thk[i, :, :]) * dx * dx * 910 / 1e12)
    iceVolume.append(np.sum(thk[i, :, :]) * dx * dx)

iceVolume = np.array(iceVolume) / 1e15
#
#
# compute trend
start = args.trendstart
ttime = np.arange(0, nTimesteps)
trend = np.polyfit(ttime[start:], iceVolume[start:], 1)
print("trend:")
print(trend)
trendGtons = trend[0] * 1e15 * 910 / 1e12
print(trendGtons, "Gt/yr")

trendline = np.arange(0, nTimesteps) * trend[0] + trend[1]

# runoffMean = np.mean(runoff) * np.ones_like(runoff)
# accumulationMean = np.mean(accumulation) * np.ones_like(accumulation)

# for i in range(12):
#     precipitation.append(np.sum(precEra5[i, :, :]) * dx * dx / 1e12)

fig, (ax2) = plt.subplots(1, 1, sharey=False, figsize=(6, 6))

ax2.plot(iceVolume, label='Ice volume (Mio km^2)')
ax2.plot(trendline, label='trend')
# ax2.plot(accumulation, label='accumulation (Gt/yr)')
# ax2.plot(accumulationMean, label='mean accumulation (Gt/yr)')
# ax2.plot(runoff, label='runoff (Gt/yr)')
# ax2.plot(runoffMean, label='mean runoff (Gt/yr)')
# ax2.plot(precipitation, label='precipitation ERA5 (Gt/yr)')

# literature values
# RACMO2

ax2.axhline(y=2.93)

ax2.legend()
ax2.set_title(expName)
# ax2.set_ylim(0, 2100)

plt.savefig(args.netcdf + "result_mot" + ".png", dpi=300)
