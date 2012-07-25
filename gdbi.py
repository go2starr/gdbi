"""
gdbi.py - A python interface to gdb
"""
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

# Need to export the path where RPyC and packaged modules are included
# so that gdb has access to them.
# TODO:  Is there a better way to do this?
if 'PAR_UNPACK_DIR' in os.environ:
    os.environ['PYTHONPATH'] = os.environ['PAR_UNPACK_DIR']

class GDBInterface(object):
    """A context wherein there is an active gdb process, and the
    remote gdb module is imported locally.

    Usage:
    with GDBInterface(opts=['a.out','dumpfile']) as gdb:
        gdb.execute('...')
        gdb.parse_and_eval('...')
    """

    GDB_PATH=['gdb']
    GDB_OPTS=[]
    GDB_APPEND=['--quiet', '-x', SERVER_PATH]

    def __init__(self, gdb=GDB_PATH, opts=GDB_OPTS, hostname=DEFAULT_HOSTNAME,
                 port=DEFAULT_SERVER_PORT, verbose=False, logger=None):
        # Logging
        if not logger:
            logging.basicConfig()
            logger = logging.getLogger()
        self.logger = logger

        # GDB
        self.argv = gdb + opts + self.GDB_APPEND
        self.verbose = verbose

        # RPyC
        self.hostname = hostname
        self.port = port
        self.proc = None
        self.conn = None

    def __enter__(self):
        try:
            self._start()
            self._connect()

            # If another instance of gdbi server was running, a
            # connection will be made, but our gdb process will have exited
            if self.proc.poll() != None:
                raise Exception('Another RPyC server already running')

            return self._import_gdb()
        except Exception:
            self._stop()
            raise

    def logged_exception(msg):
        """Logs, then re-raises exceptions"""
        def wrap(f):
            def wrapped_f(*args, **kwargs):
                try:
                    f(*args, **kwargs)
                except Exception:
                    self.logger.exception(msg)
                    raise
            return wrapped_f
        return wrap

    @logged_exception("Error starting gdb")
    def _start(self):
        """Starts gdb and runs an RPyC server within gdb's python
        interpreter. This server exposes it's gdb module."""
        fd = None
        if not self.verbose:
            fd = open(os.devnull,"rw")
        self.proc = subprocess.Popen(self.argv, stdin=fd, stdout=fd, stderr=None)

    @logged_exception("Error connecting to rpyc server")
    def _connect(self):
        """Connects to the RPyC server"""
        for i in range(SERVER_TIMEOUT):
            time.sleep(1)
            try:
                self.conn = rpyc.connect(self.hostname, self.port)
                return
            except socket.error as e:
                pass
        raise e

    @logged_exception("Error retreiving remote gdb object")
    def _import_gdb(self):
        """Retreives and imports the remote gdb module"""
        gdb = self.conn.root.exposed_gdb()
        sys.modules['gdb'] = gdb
        return gdb

    def _stop(self):
        try:
            self.proc.kill()
        except OSError, AttributeError:
            pass
        if 'gdb' in sys.modules:
            sys.modules.pop('gdb')

    def __exit__(self, type, value, traceback):
        self._stop()

