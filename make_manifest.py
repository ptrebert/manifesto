#!/usr/bin/env python3

import os
import argparse
import subprocess as sp
import multiprocessing as mp


def parse_command_line():

    default_path = os.getcwd()
    subdir = os.path.basename(default_path)
    default_manifest_file = os.path.join(os.getcwd(), 'MANIFEST_' + subdir + '.tsv')

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path',
        '-p',
        type=str,
        dest='path',
        default=default_path,
        help='Base path for manifest creation. Default: {}'.format(default_path)
    )
    parser.add_argument(
        '--manifest',
        '-m',
        type=str,
        dest='manifest',
        default=default_manifest_file,
        help='Output path for manifest file. Default: {}'.format(default_manifest_file)
    )
    parser.add_argument(
        '--jobs',
        '-j',
        type=int,
        dest='jobs',
        default=mp.cpu_count(),
        help='Number of jobs to run in parallel. Default: {}'.format(mp.cpu_count())
    )
    parser.add_argument(
        '--follow-linked-dirs',
        '-fld',
        action='store_true',
        default=False,
        dest='follow_dirs',
        help='Follow sym linked directories. Default: False'
    )
    args = parser.parse_args()

    if args.path != default_path and args.manifest == default_manifest_file:
        full_path = os.path.abspath(args.path).rstrip('/')
        subdir = os.path.basename(full_path)
        adapted_manifest_path = os.path.join(full_path, 'MANIFEST_' + subdir + '.tsv')
        setattr(args, 'manifest', adapted_manifest_path)

    return args


def compute_manifest_stats(file_loc):

    file_name, file_path = file_loc
    file_size = os.stat(file_path).st_size

    output = sp.check_output('md5sum {}'.format(file_path), shell=True, stderr=sp.STDOUT)
    try:
        md5, _ = output.decode('utf-8').split()
    except ValueError:
        raise ValueError('Computing md5 failed {}: {}'.format(file_name, output.decode('utf-8')))
    return file_name, str(file_size), md5


def main():

    args = parse_command_line()

    file_collection = []

    replace_path = os.path.split(os.path.abspath(args.path).rstrip('/'))[0]

    for root, dirs, files in os.walk(os.path.abspath(args.path), followlinks=args.follow_dirs):
        for f in files:
            if f == 'make_manifest.py':
                continue
            full_path = os.path.join(root, f)
            if os.path.islink(full_path):
                file_path = os.path.abspath(os.path.realpath(full_path))
            elif os.path.isfile(full_path):
                file_path = full_path
            else:
                # ?
                continue
            manifest_entry = full_path.replace(replace_path, '').strip('/')
            file_collection.append((manifest_entry, file_path))

    manifest_rows = []
    with mp.Pool(args.jobs) as pool:
        resit = pool.imap_unordered(compute_manifest_stats, file_collection)
        for res in resit:
            manifest_rows.append('\t'.join(res))

    with open(args.manifest, 'w') as table:
        _ = table.write('\n'.join(sorted(manifest_rows)))


if __name__ == '__main__':
    main()
