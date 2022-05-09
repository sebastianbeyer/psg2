#!/usr/bin/env python3

from collections import OrderedDict
import argparse
import matplotlib.pyplot as plt
import cmocean.cm as cmo
import numpy as np
import os
import natsort
from netCDF4 import Dataset
from matplotlib import cm

from scipy import signal
secondsperyear = 60*60*24*365

parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str, default="./results/")
args = parser.parse_args()

directory = os.fsencode(args.directory)

fileList = os.listdir(directory)
fileList = natsort.natsorted(fileList, alg=natsort.ns.IGNORECASE)
i = 0


data_list = []
for file in fileList:
    filename = os.fsdecode(file)
    if filename.startswith("ts_") and filename.endswith(".nc"):
        current_file = os.path.join(args.directory, filename)
        # print(current_file)
        data = Dataset(current_file, mode='r')

        sealevel = data.variables['sea_level_rise_potential'][:]
        time = data.variables['time'][:]
        conf = data.variables['pism_config']
        # varValue = conf.getncattr('stress_balance.sia.enhancement_factor')
        # varValue = conf.getncattr(args.variable)
        data.close()

        orig_size = len(sealevel)
        if (len(sealevel) < 400):
            continue

        sealevel = sealevel[400:]
        time = time[400:]
        time_years = time / secondsperyear
        sealevel_detrended = signal.detrend(sealevel)
        # ice_volume = ice_volume_detrended

        time_ka = time/secondsperyear / 1000

        dt = time_years[5] - time_years[4]

        # FFT
        samplingFrequency = 1/dt
        fourierTransform = np.fft.fft(
            sealevel_detrended)/len(sealevel_detrended)  # Normalize amplitude
        fourierTransform = fourierTransform[range(
            int(len(sealevel_detrended)/2))]  # Exclude sampling frequency

        tpCount = len(sealevel)
        values = np.arange(int(tpCount/2))
        timePeriod = tpCount/samplingFrequency
        frequencies = values/timePeriod
        # print(f"dt: {dt} years")
        # print(f"sampling frequency: {samplingFrequency}")
        # print(f"sampling interval : {1/samplingFrequency} years")

        # find maximum
        main_freq_index = np.argmax(abs(fourierTransform))
        main_period = 1/frequencies[main_freq_index]
        main_amplitude = abs(fourierTransform[main_freq_index])

        # find second max
        second_index = np.argsort((abs(fourierTransform)))[-2]
        second_period = 1/frequencies[second_index]
        second_amplitude = abs(fourierTransform[second_index])

        data_list.append(
            {"file": current_file,
             "main_amp": main_amplitude,
             "orig_length": orig_size,
             "main_period": main_period,
             "second_period": second_period,
             "second_amp": second_amplitude,
             })
        # print(main_period, main_amplitude, current_file)

# sorted_list = sorted(data_list, key=lambda d: d['main_period'])
sorted_list = sorted(data_list, key=lambda d: d['main_amp'])

print("first period largest between 800 and 18000 years")
for entry in sorted_list:
    if entry["orig_length"] > 500 and entry["main_period"] > 800 and entry["main_period"] < 18000:
        # print(entry["main_period"], entry["main_amp"],
        #       entry["orig_length"], entry["file"])
        main_period = entry["main_period"]
        main_amp = entry["main_amp"]
        second_period = entry["second_period"]
        second_amp = entry["second_amp"]
        orig_length = entry["orig_length"]
        file = entry["file"]
        print(f"{main_period:10.2f} {main_amp:4.2f} {second_period:10.2f} {second_amp:4.2f} {orig_length:5d} {file}")

print("second period largest between 800 and 18000 years")
for entry in sorted_list:
    if entry["orig_length"] > 500 and entry["second_period"] > 800 and entry["second_period"] < 18000:
        # print(entry["main_period"], entry["main_amp"],
        #       entry["orig_length"], entry["file"])
        main_period = entry["main_period"]
        main_amp = entry["main_amp"]
        second_period = entry["second_period"]
        second_amp = entry["second_amp"]
        orig_length = entry["orig_length"]
        file = entry["file"]
        print(f"{main_period:10.2f} {main_amp:4.2f} {second_period:10.2f} {second_amp:4.2f} {orig_length:5d} {file}")
# import json
# print (json.dumps(sorted_list, indent=2))

# print(sorted_list)

# print(f"main period: {main_period} years")
# print(f"main amplitude: {main_amplitude}")
