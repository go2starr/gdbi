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
if 'PAR_UNPACK_DIR' in os.environ:
    os.environ['PYTHONPATH'] = os.environ['PAR_UNPACK_DIR']

class GDBInterface(object):
    """This module provides a

    Usage:
    with GDBInterface(opts=['opts','here']) as gdb:
        gdb.execute('...')
        gdb.parse_and_eval('...')
    """

    def __init__(self, logger=None, gdb=GDB_PATH, opts=GDB_OPTS, hostname=DEFAULT_HOSTNAME,
                 port=DEFAULT_SERVER_PORT, verbose=False):
        # Logging
        if not logger:
            logger = logging.getLogger()
        self.logger = logger

        # GDB
        self.argv = gdb + opts + GDB_APPEND
        self.verbose = verbose

        # RPyC
        self.hostname = hostname
        self.port = port
        self.proc = None
        self.conn = None

    def __enter__(self):
        """A gdb subprocess with rpyc server context"""
        try:
            try:
                self._start()
            except:
                self.logger.exception("Error starting gdb: %s" % self.argv)
                raise
            try:
                self._connect()
            except:
                self.logger.exception("Error connecting to RPyC server")
                raise

            # If another instance of gdbi server was running, a
            # connection will be made, but our gdb process will have exited
            if self.proc.poll() != None:
                raise Exception('Another RPyC server already running')

            try:
                return self._import_remote_gdb()
            except:
                self.logger.exception("Error retreiving remote gdb object")
                raise
        except:
            self._stop()
            raise

    def _start(self):
        """Start GDB and RPyC server"""
        fd = None
        if not self.verbose:
            fd = open(os.devnull,"rw")
        self.proc = subprocess.Popen(self.argv, stdin=fd, stdout=fd)

    def _connect(self):
        """Connect to RPyC server"""
        def __connect():
            self.conn = rpyc.connect(self.hostname, self.port)

        for i in range(SERVER_TIMEOUT):
            time.sleep(1)
            try:
                __connect()
                return
            except socket.error:
                pass
        __connect()

    def _import_remote_gdb(self):
        """Import remote gdb object"""
        gdb = self.conn.root.exposed_gdb()
        sys.modules['gdb'] = gdb
        return gdb

    def _stop(self):
        """Kill gdb process"""
        try:
            self.proc.kill()
        except OSError, AttributeError:
            pass
        try:
            sys.modules.pop('gdb')
        except KeyError:
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
    args = sys.argv[1:]

    # Arg format is: <gdbi_args> -- <gdb_args>
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
