#!/bin/env python
"""
gdbi.py - An interface to gdb's python interpreter
"""
import __builtin__
import time
import sys
import os
import inspect
import subprocess
import rpyc

DEFAULT_HOSTNAME='localhost'
DEFAULT_SERVER_PORT=18861

SERVER_PATH='/home/mstarr/dev/gdbi/server.py' ## TODO: From package location
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

    def patch(self):
        argv = self.gdb + self.opts + self.append
        print self.gdb
        print argv
        self._run(argv)
        self._connect()
        self._patch()

    def _run(self, argv):
        print 'Running', argv
        fd = open("/dev/null","rw")
        self.proc = subprocess.Popen(argv, stdin=fd, stdout=fd)

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

