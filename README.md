## Pism Setup Generator

This is a bunch of scripts to generate reproducable run setups for PISM
It uses yaml from different files to combine the commands.


To list available experiments you need to

`./src/main.py list exps`

Experiment setups live in files under the setups directory. They can be in any
yaml file, but they need to be below an `experiments:` parent.

so, if you want to make a new experiment, you can just make a new file in
`./setups/`


```
experiments:
  NEW_EXPERIMENT:
    pism-command-line-option: value for that option
    pism-command-line-option: value for that other option
```

Then you run

`./src/main.py generate NEW_EXPERIMENT --copy_config`

and a runfile will be generated using a template (runfile templates are in
`./runfile_templates`).

### Example

Let's try that:

Make a new file: `./setups/experiments_sebastian_LGM.yaml`
```
experiments:
  SB_LGM_firsttry:
    i: /home/sbeyer/datasets/test/file_prepared_for_pism.nc
    Mx: 76
    My: 141
    Mz: 101
    Mbz: 11
    Lz: 4000
    Lbz: 2000
    ys: -10000
    ye: 0
    surface: given
    front_retreat_file: /home/sbeyer/datasets/test/oceankill.nc
    sia_e: 5.0
    stress_balance: ssa+sia
    topg_to_phi: 5.0,40.0,-300.0,700.0
    pseudo_plastic: YES
    pseudo_plastic_q: 0.4
    till_effective_fraction_overburden: 0.02
```

Now you can `./src/main.py generate SM_LGM_firsttry --copy_config`

And you should get a runfile in `./experiments/SB_LGM_firsttry/`

Now you can just cd into that directory and execute the runfile.


## submodules

So far there was not much improvement over just writing the runfile yourself,
therefore it is possible to define submodules(?better name?) and reuse them.
These are the ones that are currently implemented:

- climates
- grids
- icedynamics
- oceans
- times

you can use the stuff that is in there by writing the following into your
experiment definition:

```
experiments:
  SB_LGM_firsttry:
    i: /home/sbeyer/datasets/test/file_prepared_for_pism.nc
    grid: "{{grids.NHEM-20km-100vert}}"
    ocean: "{{oceans.flo-calving-th}}"
    climate: "{{climates.pdd-mprange}}"
    icedynamic: "{{icedynamics.lowMinPhi}}"
    time: "{{times.50k-out100-more}}"

```

then these will be replaced with the appropriate submodules(?name?).
You still need to add options for needed files, because they are not constant
for every run. (Maybe there is a better solution)

```
    ocean_th_file: $WORK/automaticIceData/output/MPI_LGM_STD_NHEM20km/MPI_LGM_STD_NHEM20km_4PISM_.nc
    front_retreat_file: $WORK/datasets/oceankillmask/NHEM_ocean_kill_20km.nc
    atmosphere_given_file: $WORK/automaticIceData/output/MPI_LGM_STD_NHEM20km/MPI_LGM_STD_NHEM20km_4PISM_.nc
    atmosphere_lapse_rate_file: $WORK/automaticIceData/output/MPI_LGM_STD_NHEM20km/PMIP_MPI_ESM_atmo_atmo_NHEM_20km.nc_ref_height.nc
    pdd_sd_file: $WORK/automaticIceData/output/MPI_LGM_STD_NHEM20km/MPI_LGM_STD_NHEM20km_4PISM_.nc
    pdd_sd_period: 1
```


## parameter studies

todo

## plots

There are some plotting routines in `./plotscripts/` they are not great, but
some might be a useful starting point


