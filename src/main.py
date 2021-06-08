#!/usr/bin/env python3

import os
import stat
import sys
import argparse
from shutil import copyfile
import pprint
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from himl import ConfigProcessor
from time import asctime
import jinja2
from pathlib import Path

import version
import paths

# get location of this stuff and add the paths, so no install is necessary
psg_file = os.path.realpath(os.path.expanduser(__file__))
# psg_prefix = os.path.dirname(os.path.dirname(psg_file))

sys.path.insert(0, paths.psg_src_path)


def load_yaml(setups_path):
    config_processor = ConfigProcessor()
    tree = config_processor.process(path=setups_path,
                                    filters=(),
                                    exclude_keys=(),
                                    output_format="yaml",
                                    print_data=False)

    # use the simple yaml to read without interpolation
    psg_exp_file = os.path.join(setups_path, "experiments.yaml")
    stream = open(psg_exp_file, 'r')
    tree_nointerp = load(stream, Loader=Loader)
    return tree, tree_nointerp


def listCmd(args):
    tree, tree_nointerp = load_yaml(paths.setups_path)
    if args.type == 'exps':
        for key, value in tree_nointerp['experiments'].items():
            print(key)


def rsync_command(args):
    import subprocess
    experiment = args.experiment
    remote = args.remote
    if remote == 'cluster':
        path = '/home/sbeyer'
    else:
        path = '/work/sbeyer'
    if remote == 'hlrn':
        path = "/scratch/usr/hbkbasti"
    if remote == 'hlrng':
        path = "/scratch/usr/hbkbasti"
    source = remote + ":" + path + "/psg2/experiments/" + experiment + "/*.nc"
    destination = os.path.join(paths.exp_envs_path, experiment)
    subprocess.call(["rsync", "--progress", "-avzh", source, destination])
    # rsync --progress -avzh k19:/work/sbeyer/psg/experiments/LGM-NHEM-40km-constant-siaEtuning/ts_LGM-NHEM-40km-constant-siaEtuning_sia_e_3.nc .


def load_psg2_config():
    stream = open(paths.psg2_config_file, 'r')
    psg2_config = load(stream, Loader=Loader)
    return psg2_config


def flatten_dict(d):
    """
    This makes the dict of dicts for the model description into a single
    list that can be converted to PISM cmd line parameters
    """
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    # yield key + "." + subkey, subvalue
                    yield subkey, subvalue
            else:
                yield key, value

    return dict(items())


def add_filenames_to_tree(name, tree, stagetag=""):
    outFile = os.path.join(
        paths.exp_envs_path,
        name,
        name + stagetag + '.nc',
    )
    tsFile = os.path.join(
        paths.exp_envs_path,
        name,
        'ts_' + name + stagetag + '.nc',
    )
    extraFile = os.path.join(
        paths.exp_envs_path,
        name,
        'ex_' + name + stagetag + '.nc',
    )
    runscriptFile = os.path.join(
        paths.exp_envs_path,
        tree['name'],
        'run' + tree['name'] + stagetag + '.sh',
    )

    tree['o'] = outFile
    tree['ts_file'] = tsFile
    tree['extra_file'] = extraFile
    tree['runscript_file'] = runscriptFile


def append_tree_options_to_file(tree, out_file):
    """
    """
    noWriteKeys = ["name", "n_procs", "runscript_file", "setup", "partition",
                   "timelimit", "nnodes", "ntasks", "account", "pism_module", "mail"]
    with open(out_file, 'a') as f:
        for key, value in tree.items():
            if key not in noWriteKeys:
                line = "-{} {} \\".format(key, value)
                # print(line)
                f.write('  ' + line + '\n')


def write_to_file(tree, templateName):
    out_file = tree['runscript_file']
    directory = os.path.split(out_file)[0]
    Path(directory).mkdir(parents=True, exist_ok=True)

    loader = jinja2.FileSystemLoader(searchpath=paths.templates_path)
    env = jinja2.Environment(loader=loader,
                             trim_blocks=True,
                             undefined=jinja2.StrictUndefined)

    basedata = {
        'exp_name': tree['name'],
        'psg_revision': version.git_version(),
        'timestamp': asctime(),
        'partition': tree['partition'],
        'timelimit': tree['timelimit'],
        'nnodes': tree['nnodes'],
        'ntasks': tree['ntasks'],
        'account': tree['account'],
        'n_procs': tree['n_procs'],
        'pism_module': tree['pism_module'],
        'mail': tree['mail'],
    }
    template = env.get_template(templateName)
    template.stream(basedata).dump(out_file)
    print('Writing runfile to {}'.format(out_file))
    append_tree_options_to_file(tree, out_file)


def make_file_executable(tree):
    """Need to read stats first to just add"""
    out_file = tree['runscript_file']
    st = os.stat(out_file)
    os.chmod(out_file, st.st_mode | stat.S_IEXEC)


def merge_with_default(setups, single_setup):
    default = setups['experiments']['default']
    default.update(single_setup)
    single_setup = default
    return single_setup


def add_name_to_setup(setup, name):
    setup['name'] = name
    return setup


def handle_parameter_study(setup, stagetag=""):
    """This returns a list of setups, only one when there is no study.
    Stagetag is only nonempty for (grid)sequences
    """
    setup_list = [setup]
    for key, value in setup.items():
        if isinstance(value, list):
            setup_list = []  # empty again
            print("Found parameter study: {}: {}".format(key, value))
            for parameter in value:
                new_setup = setup.copy()
                # print(parameter)
                new_setup[key] = parameter

                # handle the new file names
                new_setup['o'] = os.path.join(
                    paths.exp_envs_path,
                    setup['name'],
                    setup['name'] + stagetag + "_param-" + key + "-" +
                    str(parameter) + '_.nc',
                )
                new_setup['ts_file'] = os.path.join(
                    paths.exp_envs_path,
                    setup['name'],
                    'ts_' + setup['name'] + stagetag + "_param-" + key +
                    "-" + str(parameter) + '_.nc',
                )
                new_setup['extra_file'] = os.path.join(
                    paths.exp_envs_path,
                    setup['name'],
                    'ex_' + setup['name'] + stagetag + "_param-" + key +
                    "-" + str(parameter) + '_.nc',
                )
                new_setup['runscript_file'] = os.path.join(
                    paths.exp_envs_path,
                    setup['name'],
                    'run_' + setup['name'] + stagetag + "_param-" + key +
                    "-" + str(parameter) + '_.sh',
                )

                setup_list.append(new_setup)
    # pprint.pprint(setup_list)
    return setup_list


def write_allruns(runscripts):
    """
    Writes a bash script which runs all runs of sequence or param study
    """
    allrunFile = os.path.dirname(runscripts[0]) + "/runall.sh"
    with open(allrunFile, 'w') as rsh:
        rsh.write('''\
#! /bin/bash
# psg2 runfile
set -e
''')
    with open(allrunFile, 'a') as f:
        for runscript in runscripts:
            line = "./{} ".format(os.path.basename(runscript))
            f.write('' + line + '\n')

    st = os.stat(allrunFile)
    os.chmod(allrunFile, st.st_mode | stat.S_IEXEC)


def is_study(setup_list):
    return len(setup_list) > 1


def handle_automaticData(tree, config):
    if "automaticData" in tree:
        print("found automaticData in setup")
    # need to have a default set of stuff to include and then have an
    # option with "+this ~that"...
    # also need to check which variables are found automatically and which
    # need explicit mention
    # ocean_th_file
    # front_retreat_file
    # atmosphere_given_file
    # atmosphere_lapse_rate_file
    # pdd_sd_file
    tree["i"] = os.path.join(config["automaticData_path"], "output",
                             tree["automaticData"], tree["automaticData"] + "_4PISM_.nc")
    # check if file exists
    print(tree["i"])
    my_file = Path(tree["i"])
    if my_file.is_file():
        print("jo it exists!")
    else:
        print("no it does not exist")


def generate_command(args):
    """This runs when the generate command is given on the command line
    """
    psg2_config = load_psg2_config()
    print(psg2_config)
    name = args.exp
    all_setups, _ = load_yaml(paths.setups_path)
    single_setup = flatten_dict(all_setups['experiments'][name])
    single_setup = add_name_to_setup(single_setup, name)

    single_setup = merge_with_default(all_setups, single_setup)
    add_filenames_to_tree(name, single_setup)

    handle_automaticData(single_setup, psg2_config)

    # set some stuff from config file
    if "slurm_mail" in psg2_config:
        single_setup["mail"] = psg2_config["slurm_mail"]
    if "template_default" in psg2_config:
        runfile_template = psg2_config["template_default"]
    else:
        runfile_template = args.runfile_template

    # check parameter studies
    setup_list = handle_parameter_study(single_setup)
    for setup in setup_list:
        write_to_file(setup, runfile_template)
        make_file_executable(setup)
    if args.copy_config or psg2_config['always_copy_config']:
        print("copied config file into experiment folder")
        out_file = setup['runscript_file']
        out_dir = os.path.dirname(out_file)
        copyfile(os.path.join(paths.pism_config_path, 'pism_config.nc'),
                 os.path.join(out_dir, 'pism_config.nc'))


def sequence_command(args):
    """This runs when the sequence command is given on the command line
    """
    name = args.seq
    runfile_template = args.runfile_template
    all_setups, _ = load_yaml(paths.setups_path)
    sequence = flatten_dict(all_setups['sequences'][name])
    sequence = add_name_to_setup(sequence, name)
    sequence = merge_with_default(all_setups, sequence)
    # pprint.pprint(sequence)

    # remove stages from tree and save separately
    stages = sequence['stages']
    del sequence['stages']

    runscripts = []
    for i, stage in enumerate(stages):
        add_filenames_to_tree(name, sequence, "_stage{}".format(i))
        if i > 0:
            sequence['regrid_file'] = prev_stage_output
        # remember output for next stage
        prev_stage_output = sequence['o']

        # print(stage)
        del stage['stage']  # remove stage variable...
        stage_flat = flatten_dict(stage)
        sequence_copy = sequence.copy()

        # update setup with stage parameters
        sequence_copy.update(stage_flat)
        # pprint.pprint(sequence_copy)

        # check parameter studies
        setup_list = handle_parameter_study(sequence_copy,
                                            "_stage{}".format(i))

        for setup in setup_list:
            runscripts.append(setup['runscript_file'])
            write_to_file(setup, runfile_template)
            make_file_executable(setup)

    write_allruns(runscripts)
    if args.copy_config:
        print("copied config file into experiment folder")
        out_file = setup['runscript_file']
        out_dir = os.path.dirname(out_file)
        copyfile(os.path.join(paths.pism_config_path, 'pism_config.nc'),
                 os.path.join(out_dir, 'pism_config.nc'))


parser = argparse.ArgumentParser(description='Generate pism runs')
# parser.add_argument('exp', help='name of the experiment', type=str)

subparsers = parser.add_subparsers()

parser_list = subparsers.add_parser('list')
parser_list.add_argument('type', choices=['exps', 'sub'])
parser_list.set_defaults(func=listCmd)

parser_generate = subparsers.add_parser('generate')
parser_generate.add_argument('exp')
parser_generate.add_argument('--runfile_template',
                             default="PISM_bash.sh",
                             choices=["PISM_bash.sh", "PISM_SLURM.sh"])
parser_generate.add_argument('--copy_config',
                             action='store_true',
                             help="copy the default config into experiment folder")
parser_generate.set_defaults(func=generate_command)

parser_generate = subparsers.add_parser('sequence')
parser_generate.add_argument('seq')
parser_generate.add_argument('--runfile_template',
                             default="PISM_bash.sh",
                             choices=["PISM_bash.sh", "PISM_SLURM.sh"])
parser_generate.add_argument('--copy_config',
                             action='store_true',
                             help="copy the default config into experiment folder")
parser_generate.set_defaults(func=sequence_command)

parser_rsync = subparsers.add_parser('rsync')
parser_rsync.add_argument('experiment')
parser_rsync.add_argument('--remote',
                          default='k19',
                          choices=['k19', 'cluster', 'hlrn', 'hlrng'])
parser_rsync.set_defaults(func=rsync_command)

args = parser.parse_args()
args.func(args)
