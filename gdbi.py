#!/bin/env python
"""
gdbi.py - An interface to gdb's python interpreter
"""
import sys
import rpyc
import subprocess

DEFAULT_GDB='gdb'
DEFAULT_GDB_OPTS=[]
GDB_APPEND=['-x', 'server.py']

class GDBi(object):
    def run(self, gdb=DEFAULT_GDB, opts=DEFAULT_GDB_OPTS):
        argv = [gdb] + opts + GDB_APPEND
        self.proc = subprocess.Popen(argv)
        self.proc.wait()

    def stop(self):
        try:
            self.proc.kill()
        except OSError:
            pass
        
if __name__ == '__main__':
    gdbi = GDBi()
    try:
        gdbi.run(opts = sys.argv[1:])
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        gdbi.stop()

