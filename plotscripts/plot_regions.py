#!/usr/bin/env python3

from tqdm import tqdm
from typing import List
from dataclasses import dataclass
import argparse
import matplotlib.pyplot as plt
import cmocean.cm as cmo
import numpy as np

from netCDF4 import Dataset

parser = argparse.ArgumentParser()
parser.add_argument('netcdf', type=str)
parser.add_argument('regionfile',
                    type=str)
parser.add_argument('outfile',
                    type=str)
args = parser.parse_args()

ncName = args.netcdf
expName = ncName.split('/')[-1]


print("loading file...")
data = Dataset(ncName, mode='r')
x = data.variables['x'][:]
y = data.variables['y'][:]
time = data.variables['time'][:]

# convert to years
time = time / (60*60*24*365) / 1000

thk = data.variables['thk'][:]
# vel = data.variables['velsurf_mag'][:]
# acc = data.variables['surface_accumulation_flux'][:]
# run = data.variables['surface_runoff_flux'][:]
# maskPISM = data.variables['mask'][:]
data.close()
print("loaded experiment file")

dx = x[1] - x[0]
nTimesteps = thk.shape[0]

print(thk.shape)

# load region file:
data_regions = Dataset(args.regionfile, mode='r')
regions = data_regions.variables['polygon'][:]
regi = data_regions.variables['polygon']
regionNames = regi.flag_meanings.split(",")
data_regions.close()

print("loaded region file")

print(regionNames)
nRegions = len(regionNames)


def sea_level_rise_potential(volume):
    # volume = ice_volume_not_displacing_seawater(geometry, thickness_threshold)
    water_density = 1000
    ice_density = 910
    ocean_area = 362.5e6  # km ^ 2  cogley2010
    ocean_area = 362.5e12  # m ^ 2  cogley2010

    additional_water_volume = (ice_density / water_density) * volume
    sea_level_change = additional_water_volume / ocean_area
    return sea_level_change

################################


@dataclass
class RegionData:
    name: str
    id: int
    icemass: List
    icevolume: List
    mask: np.ndarray
    surfaceArea: float


allRegions = []
for i in range(nRegions):
    mask = regions == i
    surfaceArea = np.sum(mask) * dx**2 * 1e-6  # in km^2
    allRegions.append(
        RegionData(
            name=regionNames[i],
            id=i,
            icemass=[],
            icevolume=[],
            mask=mask,
            surfaceArea=surfaceArea,
        )
    )

# print(allRegions)

for t in tqdm(range(nTimesteps)):
    for i in range(nRegions):
        # print(i)
        currentRegion = allRegions[i]
        mask = currentRegion.mask
        # region_thk = mask*thk
        current_thk = thk[t, :, :]*mask
        # print(np.sum(current_thk))
        volume = np.sum(current_thk) * dx**2
        currentRegion.icevolume.append(volume)
        mass = np.sum(current_thk) * dx**2 * 910/1e12
        currentRegion.icemass.append(mass)

        # allRegions[i].icemass.append(
        #     np.sum(region_thk[i, :, :]) * dx * dx * 910 / 1e12)
        # iceVolume.append(np.sum(region_thk[i, :, :]) * dx * dx)


# iceVolume = np.array(iceVolume) / 1e15
#
#

fig, (ax1) = plt.subplots(1, 1, sharey=False, figsize=(6, 6))

for i in range(nRegions):
    currentRegion = allRegions[i]
    mass = currentRegion.icemass
    volume = currentRegion.icevolume

    sealevel = sea_level_rise_potential(np.array(volume))

    ax1.plot(time, sealevel, label=currentRegion.name)
ax1.set_xlabel("Time in ka")
# ax2.plot(trendline, label='trend')


# ax2.plot(accumulation, label='accumulation (Gt/yr)')
# ax2.plot(accumulationMean, label='mean accumulation (Gt/yr)')
# ax2.plot(runoff, label='runoff (Gt/yr)')
# ax2.plot(runoffMean, label='mean runoff (Gt/yr)')
# ax2.plot(precipitation, label='precipitation ERA5 (Gt/yr)')

# literature values
# RACMO2

# ax1.axhline(y=2.93)

ax1.legend()

plt.savefig(args.outfile, dpi=300)
plt.show()
# ax1.set_title(expName)
# ax2.set_ylim(0, 2100)
