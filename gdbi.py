#!/bin/env python
"""
gdbi.py - An interface to gdb's python interpreter
"""
import __builtin__
import time
import sys
import subprocess
import rpyc

from conf import DEFAULT_HOSTNAME
from conf import DEFAULT_SERVER_PORT

DEFAULT_GDB=['gdb']
DEFAULT_GDB_OPTS=[]

GDB_APPEND=['-x', 'server.py']
GDB_TIMEOUT=10

class GDBInterface(object):
    def __init__(self, gdb=DEFAULT_GDB, opts=DEFAULT_GDB_OPTS,
                 hostname=DEFAULT_HOSTNAME, port=DEFAULT_SERVER_PORT):
        self.gdb = gdb
        self.opts = opts
        self.hostname = hostname
        self.port = port
        self.proc = None
        self.conn = None

    def patch(self):
        argv = self.gdb + self.opts + GDB_APPEND
        self._run(argv)
        self._connect()
        self._patch()

    def _run(self, argv):
        fd = open("/dev/null","rw")
        self.proc = subprocess.Popen(argv, stdin=fd, stderr=fd, stdout=fd)

    def _connect(self):
        for i in range(GDB_TIMEOUT):
            try:
                self.conn = rpyc.connect(self.hostname, self.port)
                return
            except:
                time.sleep(1)

    def _patch(self):
        __builtin__.gdb = self.conn.root.exposed_gdb()

    def stop(self):
        try:
            self.proc.kill()
        except OSError:
            pass
        
if __name__ == '__main__':
    gdbi = GDBInterface(opts = sys.argv[1:])
    try:
        gdbi.patch()

        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed()
        ipshell()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        gdbi.stop()

