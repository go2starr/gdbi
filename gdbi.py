#!/bin/env python
"""
gdbi.py - A python interface to gdb
"""
import __builtin__
import socket
import time
import sys
import os
import inspect
import subprocess
import rpyc
import logging

from kcrash.logger import get_logger

DEFAULT_HOSTNAME='localhost'
DEFAULT_SERVER_PORT=18861

SERVER_PATH=os.path.join(os.path.dirname(gdbi.__file__), 'server.py')
SERVER_TIMEOUT=10

GDB_PATH=['gdb']
GDB_OPTS=['']
GDB_APPEND=['--quiet', '-x', SERVER_PATH]

class GDBInterface(object):
    """This class returns a remote python object which is the gdb
    module of a running gdb process.  This is done by monkey-patching
    the gdb object into python's builtins.

    Usage:
    with gdb as GDBInterface(opts=['opts','here']):
        gdb.execute('...')
        gdb.parse_and_eval('...')
    """

    def __init__(self, logger, opts=GDB_OPTS, hostname=DEFAULT_HOSTNAME,
                 port=DEFAULT_SERVER_PORT):
        # Logging
        self.logger = logger

        # GDB
        self.gdb = GDB_PATH
        self.opts = opts
        self.append = GDB_APPEND
        self.argv = self.gdb + self.opts + self.append

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

            # Patch gdb into builtins
            try:
                self._patch()
            except Exception as e:
                self.logger.exception(
                    "Error retreiving remote gdb object: (%s)" % e)
                raise

            # Return remote gdb object
            return __builtin__.gdb

        except:
            self._stop()
            raise

    def _start(self, argv):
        # Need to export the path where RPyC and packaged modules are included
        os.environ['PYTHONPATH'] = os.environ['PAR_UNPACK_DIR']
        fd = open("/dev/null","rw")
        self.proc = subprocess.Popen(argv, stdin=fd, stdout=fd)

    def _connect(self):
        for i in range(SERVER_TIMEOUT):
            time.sleep(1)
            try:
                self.conn = rpyc.connect(self.hostname, self.port)
                return
            except socket.error as e:
                pass
        raise e

    def _patch(self):
        __builtin__.gdb = self.conn.root.exposed_gdb()

    def _stop(self):
        try:
            self.proc.kill()
        except OSError:
            pass

    def __exit__(self, type, value, traceback):
        __builtin__.gdb = None
        self._stop()

if __name__ == '__main__':
    g = GDBInterface(get_logger(), opts = sys.argv[1:])
    with g as gdb:
        from IPython import embed
        embed()
