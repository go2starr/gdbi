#!/bin/env python
"""
gdbi.py - A python interface to gdb
"""
import argparse
import socket
import time
import sys
import os
import subprocess
import rpyc
import logging

import gdbi

DEFAULT_HOSTNAME='localhost'
DEFAULT_SERVER_PORT=18861

SERVER_PATH=os.path.join(os.path.dirname(gdbi.__file__), 'server.py')
SERVER_TIMEOUT=10

GDB_PATH=['gdb']
GDB_OPTS=[]
GDB_APPEND=['--quiet', '-x', SERVER_PATH]

# Need to export the path where RPyC and packaged modules are included
# so that gdb has access to them.
# TODO:  Is there a better way to do this?
if os.environ.has_key('PAR_UNPACK_DIR'):
    os.environ['PYTHONPATH'] = os.environ['PAR_UNPACK_DIR']

class GDBInterface(object):
    """This class returns a remote python object which is the gdb
    module of a running gdb process.  This is done by monkey-patching
    the gdb object into python's builtins.

    Usage:
    with gdb as GDBInterface(opts=['opts','here']):
        gdb.execute('...')
        gdb.parse_and_eval('...')
    """

    def __init__(self, logger=None, opts=GDB_OPTS, hostname=DEFAULT_HOSTNAME,
                 port=DEFAULT_SERVER_PORT, verbose=False):
        # Logging
        if not logger:
            logger = logging.getLogger()
        self.logger = logger

        # GDB
        self.gdb = GDB_PATH
        self.opts = opts
        self.append = GDB_APPEND
        self.argv = self.gdb + self.opts + self.append
        self.verbose = verbose

        # RPyC
        self.hostname = hostname
        self.port = port
        self.proc = None
        self.conn = None

    def __enter__(self):
        try:
            # Start GDB and RPyC server
            try:
                self._start(self.argv)
            except Exception as e:
                self.logger.exception("Error starting gdb: (%s)" % e)
                raise

            # Connect to RPyC server
            try:
                self._connect()

                # If another instance of gdbi server was running, a
                # connection will be made, but our gdb process will have exited
                if self.proc.poll() != None:
                    raise Exception('Another RPyC server already running')
            except Exception as e:
                self.logger.exception(
                    "Error connecting to rpyc server: (%s)" % e)
                raise

            # Retreive remote gdb module
            try:
                return self.conn.root.exposed_gdb()
            except Exception as e:
                self.logger.exception(
                    "Error retreiving remote gdb object: (%s)" % e)
                raise
        except:
            self._stop()
            raise

    def _start(self, argv):
        fd = None
        if not self.verbose:
            fd = open("/dev/null","rw")
        print argv
        self.proc = subprocess.Popen(argv, stdin=fd, stdout=fd, stderr=fd)

    def _connect(self):
        for i in range(SERVER_TIMEOUT):
            time.sleep(1)
            try:
                self.conn = rpyc.connect(self.hostname, self.port)
                return
            except socket.error as e:
                pass
        raise e

    def _stop(self):
        try:
            self.proc.kill()
        except OSError, AttributeError:
            pass

    def __exit__(self, type, value, traceback):
        self._stop()

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

    # Splice args meant for gdb by '--'
    args = sys.argv[1:]
    try:
        pos = args.index('--')
        kwargs['opts'] = args[pos + 1:]
        args = args[:pos]
    except:
        pass

    # Parse args
    args = get_args(args)

    # Append path
    if args.pythonpath:
        for f in args.pythonpath.split(':'):
            sys.path.insert(0, os.path.realpath(f))

    # Set GDB verbosity
    kwargs['verbose'] = args.verbose

    g = GDBInterface(logging.getLogger(), **kwargs)
    with g as gdb:
        from IPython import embed
        embed()
