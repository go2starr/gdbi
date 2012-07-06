"""
classic rpyc server running a SlaveServer.  This module will be run from within gdb.
"""
import gdb
import sys
import rpyc
from rpyc.utils.server import ThreadedServer
from rpyc.utils.classic import DEFAULT_SERVER_PORT
from rpyc.core import SlaveService

from conf import DEFAULT_HOSTNAME

class GDBiServer(SlaveService):
    def on_disconnect(self):
        # Hack to close the server
        server.close()

server = ThreadedServer(GDBiServer, hostname=DEFAULT_HOSTNAME, port=DEFAULT_SERVER_PORT)
        
if __name__ == "__main__":
    server.start()
    gdb.execute('quit')
