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

class GDBi(object):
    def __init__(self, gdb=DEFAULT_GDB, opts=DEFAULT_GDB_OPTS,
                 hostname=DEFAULT_HOSTNAME, port=DEFAULT_SERVER_PORT):
        self.gdb = gdb
        self.opts = opts
        self.hostname = hostname
        self.port = port
        self.proc = None
        self.conn = None

    def patch(self):
        self._run()
        self._connect()
        self._patch()

    def _run(self):
        argv = self.gdb + self.opts + GDB_APPEND
        fd = open("/dev/null","w")
        self.proc = subprocess.Popen(argv, stdout=fd, stderr=fd)

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
    gdbi = GDBi(opts = sys.argv[1:])
    try:
        gdbi.patch()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        gdbi.stop()

