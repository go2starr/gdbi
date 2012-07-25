#!/bin/env python
import argparse
from gdbi import GDBInterface

def get_parser():
    parser = argparse.ArgumentParser(usage='[OPTIONS] [-- GDB_OPTIONS]')
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="increase output verbosity")
    parser.add_argument("-p", "--pythonpath",
                        help="append to the PYTHONPATH environment variable")
    return parser

def get_args(args):
    return get_parser().parse_args(args)

if __name__ == '__main__':
    kwargs = {}

    # Args are formatted: <gdbi_opts> -- <gdb_opts>
    args = sys.argv[1:]
    if '--' in args:
        pos = args.index('--')
        kwargs['opts'] = args[pos + 1:]
        args = args[:pos]

    # Parse args
    args = get_args(args)

    # Append path
    if args.pythonpath:
        for f in args.pythonpath.split(':'):
            sys.path.insert(0, os.path.realpath(f))

    # Set GDB verbosity
    kwargs['verbose'] = args.verbose

    with GDBInterface(**kwargs) as gdb:
        from IPython import embed
        embed()
