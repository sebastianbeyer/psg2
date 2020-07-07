#!/usr/bin/env python3

import os
import stat
import sys
import argparse
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
    source = remote + ":" + path + "/psg2/experiments/" + experiment + "/*.nc"
    destination = os.path.join(paths.exp_envs_path, experiment)
    subprocess.call(["rsync", "--progress", "-avzh", source, destination])
    # rsync --progress -avzh k19:/work/sbeyer/psg/experiments/LGM-NHEM-40km-constant-siaEtuning/ts_LGM-NHEM-40km-constant-siaEtuning_sia_e_3.nc .


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


def add_filenames_to_tree(name, tree):
    outFile = os.path.join(
        paths.exp_envs_path,
        name,
        name + '.nc',
    )
    tsFile = os.path.join(
        paths.exp_envs_path,
        name,
        'ts_' + name + '.nc',
    )
    extraFile = os.path.join(
        paths.exp_envs_path,
        name,
        'ex_' + name + '.nc',
    )

    tree['o'] = outFile
    tree['ts_file'] = tsFile
    tree['extra_file'] = extraFile


def append_tree_options_to_file(tree, out_file):
    """
    """
    noWriteKeys = ["name", "n_procs"]
    with open(out_file, 'a') as f:
        for key, value in tree.items():
            if key not in noWriteKeys:
                line = "-{} {} \\".format(key, value)
                # print(line)
                f.write('  ' + line + '\n')


def write_to_file(tree, out_file, templateName):
    directory = os.path.split(out_file)[0]
    Path(directory).mkdir(parents=True, exist_ok=True)

    loader = jinja2.FileSystemLoader(searchpath=paths.templates_path)
    env = jinja2.Environment(loader=loader,
                             trim_blocks=True,
                             undefined=jinja2.StrictUndefined)

    basedata = {
        'exp_name': tree['name'],
        'psg_revision': version.git_version(),
        'n_procs': tree['n_procs'],
        'timestamp': asctime()
    }
    template = env.get_template(templateName)
    template.stream(basedata).dump(out_file)
    print('Writing runfile to {}'.format(out_file))
    append_tree_options_to_file(tree, out_file)


def runscript_file_name(tree):
    """Returns the file name of the generated runscript."""

    runscript = os.path.join(
        paths.exp_envs_path,
        tree['name'],
        'run' + tree['name'] + '.sh',
    )
    return runscript


def make_file_executable(out_file):
    """Need to read stats first to just add"""
    st = os.stat(out_file)
    os.chmod(out_file, st.st_mode | stat.S_IEXEC)


def merge_with_default(setups, treeFlat):
    default = setups['experiments']['default']
    default.update(treeFlat)
    treeFlat = default
    return treeFlat


def add_name_to_setup(setup, name):
    setup['name'] = name
    return setup


def generate_command(args):
    """This runs when the generate command is given on the command line
    """
    name = args.exp
    all_setups, _ = load_yaml(paths.setups_path)
    single_setup = flatten_dict(all_setups['experiments'][name])
    single_setup = add_name_to_setup(single_setup, name)
    single_setup = merge_with_default(all_setups, single_setup)
    add_filenames_to_tree(name, single_setup)

    runscript = runscript_file_name(single_setup)
    write_to_file(single_setup, runscript, 'PISM_bash.sh')
    make_file_executable(runscript)


parser = argparse.ArgumentParser(description='Generate pism runs')
# parser.add_argument('exp', help='name of the experiment', type=str)

subparsers = parser.add_subparsers()

parser_list = subparsers.add_parser('list')
parser_list.add_argument('type', choices=['exps', 'sub'])
parser_list.set_defaults(func=listCmd)

parser_generate = subparsers.add_parser('generate')
parser_generate.add_argument('exp')
parser_generate.set_defaults(func=generate_command)

parser_rsync = subparsers.add_parser('rsync')
parser_rsync.add_argument('experiment')
parser_rsync.add_argument('--remote',
                          default='k19',
                          choices=['k19', 'cluster'])
parser_rsync.set_defaults(func=rsync_command)

args = parser.parse_args()
args.func(args)
