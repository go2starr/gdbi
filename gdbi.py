#!/bin/env python
"""
gdbi.py - An interface to gdb's python interpreter
"""
import __builtin__
import socket
import time
import sys
import os
import inspect
import subprocess
import rpyc

import gdbi
from conf import DEFAULT_HOSTNAME, DEFAULT_SERVER_PORT

SERVER_PATH=os.path.join(os.path.dirname(gdbi.__file__), 'server.py')
SERVER_TIMEOUT=10

GDB_PATH=['gdb']
GDB_OPTS=[]
GDB_APPEND=['-x', SERVER_PATH]

class GDBInterface(object):
    def __init__(self, opts=GDB_OPTS, hostname=DEFAULT_HOSTNAME, 
                 port=DEFAULT_SERVER_PORT):
        self.gdb = GDB_PATH
        self.append = GDB_APPEND
        self.opts = opts
        self.hostname = hostname
        self.port = port

        self.proc = None
        self.conn = None

    def __enter__(self):
        argv = self.gdb + self.opts + self.append
        self._start(argv)
        self._connect()
        self._patch()
        return __builtin__.gdb

    def _start(self, argv):
        fd = open("/dev/null","rw")
        self.proc = subprocess.Popen(argv, stdin=fd, stdout=fd)

    def _connect(self):
        for i in range(SERVER_TIMEOUT):
            try:
                self.conn = rpyc.connect(self.hostname, self.port)
                return
            except socket.error:
                time.sleep(1)


    def _patch(self):
        __builtin__.gdb = self.conn.root.exposed_gdb()

    def __exit__(self, type, value, traceback):
        __builtin__.gdb = None
        try:
            self.proc.kill()
        except OSError:
            pass
        
if __name__ == '__main__':
    g = GDBInterface(opts = sys.argv[1:])
    with g as gdb:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed()
        ipshell()
