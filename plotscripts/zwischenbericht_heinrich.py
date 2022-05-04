#!/usr/bin/env python3

from tqdm import tqdm
from typing import List
from dataclasses import dataclass
import argparse
import matplotlib.pyplot as plt
import cmocean.cm as cmo
import numpy as np
import matplotlib

from netCDF4 import Dataset

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
    'text.usetex': True,
    'figure.figsize': [3.39, 2.10],
    'font.family': 'serif',
}
matplotlib.rcParams.update(params)


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
# todo: fix this as soon as i have yield output
basal_yield = data.variables['tauc'][:] / 1000 #kPa
velocity = data.variables['velsurf_mag'][:]
tillwat = data.variables['tillwat'][:]
# acc = data.variables['surface_accumulation_flux'][:]
# run = data.variables['surface_runoff_flux'][:]
maskPISM = data.variables['mask'][:]
data.close()
print("loaded experiment file")

startpoint = 100
stoppoint = 350
time = time[startpoint:stoppoint]
thk = thk[startpoint:stoppoint, :, :]
basal_yield = basal_yield[startpoint:stoppoint, :, :]
velocity = velocity[startpoint:stoppoint, :, :]
tillwat = tillwat[startpoint:stoppoint, :, :]
maskPISM = maskPISM[startpoint:stoppoint, :, :]

dx = x[1] - x[0]
nTimesteps = thk.shape[0]

# print(thk.shape)

# load region file:
data_regions = Dataset(args.regionfile, mode='r')
regions = data_regions.variables['polygon'][:]
regi = data_regions.variables['polygon']
regionNames = regi.flag_meanings.split(",")
data_regions.close()

print("loaded region file")

print(regionNames)
# nRegions = len(regionNames)
nRegions = 1


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
    icethickness: List
    icevolume: List
    icevelocity: List
    basal_yield: List
    tillwat: List
    mask: np.ndarray
    surfaceArea: float


allRegions = []
mask = regions == 2
surfaceArea = np.sum(mask) * dx**2 * 1e-6  # in km^2
allRegions.append(
    RegionData(
        name=regionNames[2],
        id=2,
        icemass=[],
        icevolume=[],
        icethickness=[],
        icevelocity=[],
        basal_yield=[],
        tillwat=[],
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
        current_iceMask = maskPISM[t, :, :] != 2
        # region_thk = mask*thk
        current_thk = thk[t, :, :]*mask
        current_basal_yield = basal_yield[t, :, :]*mask
        current_velocity = velocity[t, :, :]*mask
        current_tillwat = tillwat[t, :, :]*mask
        # print(np.sum(current_thk))
        volume = np.sum(current_thk) * dx**2
        currentRegion.icevolume.append(volume)
        mass = np.sum(current_thk) * dx**2 * 910/1e12
        currentRegion.icemass.append(mass)

        # mask with pism mask to get proper means
        current_thk = np.ma.masked_array(current_thk, mask=current_iceMask)
        current_tillwat = np.ma.masked_array(
            current_tillwat, mask=current_iceMask)
        #
        currentRegion.icethickness.append(current_thk.mean())
        currentRegion.tillwat.append(current_tillwat.mean())
        currentRegion.basal_yield.append(np.mean(current_basal_yield))
        currentRegion.icevelocity.append(np.mean(current_velocity))

        # allRegions[i].icemass.append(
        #     np.sum(region_thk[i, :, :]) * dx * dx * 910 / 1e12)
        # iceVolume.append(np.sum(region_thk[i, :, :]) * dx * dx)


# iceVolume = np.array(iceVolume) / 1e15
#
#

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, figsize=(6, 6))

# adjust time to start from 0
time = time+50

# points to indicate phases
surgeindex = 202
surgex = time[surgeindex]
buildupindex = 178
buildupx = time[buildupindex]
stabindex = 206
stabx = time[stabindex]

for ax in [ax1, ax2, ax3, ax4]:
    ax.axvspan(24, 31, alpha=0.2, color='black')
    ax.axvline(x=buildupx, color="gray", linewidth=0.8)
    ax.axvline(x=surgex, color="firebrick", linewidth=0.8)
    ax.axvline(x=stabx, color="royalblue", linewidth=0.8)

for i in range(nRegions):
    currentRegion = allRegions[i]
    mass = currentRegion.icemass
    volume = currentRegion.icevolume
    velocity = currentRegion.icevelocity
    yield_stress = currentRegion.basal_yield
    thickness = currentRegion.icethickness
    tillwat = currentRegion.tillwat

    sealevel = sea_level_rise_potential(np.array(volume))
    surgey = thickness[surgeindex]
    buildupy = thickness[buildupindex]
    staby = thickness[stabindex]

    ax1.plot(time, thickness, label=currentRegion.name, color='k', lw=0.6)
    ax2.plot(time, tillwat, label=currentRegion.name, color='k', lw=0.6)
    ax3.plot(time, yield_stress, label=currentRegion.name, color='k', lw=0.6)
    ax4.plot(time, velocity, label=currentRegion.name, color='k', lw=0.6)

    ax1.plot(surgex, surgey, ls="", marker="o",
             label="points", color='firebrick', markersize=3)
    ax1.plot(buildupx, buildupy, ls="", marker="o",
             label="points", color='gray', markersize=3)
    ax1.plot(stabx, staby, ls="", marker="o",
             label="points", color='royalblue', markersize=3)

ax1.set_ylabel("Ice thickness(m)")
ax2.set_ylabel("Till water(m)")
ax3.set_ylabel("Basal yield stress\n (kPa)")
ax4.set_ylabel("Surface velocity\n (m/yr)")

ax4.set_xlabel("Time in ka")
# ax2.plot(trendline, label='trend')
#


# ax1.axhline(y=2.93)


plt.savefig(args.outfile, dpi=300)
plt.show()
# ax1.set_title(expName)
# ax2.set_ylim(0, 2100)
