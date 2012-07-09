"""
rpyc server to be run in gdb process
"""
import gdb
import sys
import rpyc
import socket
from rpyc.utils.server import ThreadedServer
from rpyc import Service, restricted

from gdbi.conf import DEFAULT_HOSTNAME
from gdbi.conf import DEFAULT_SERVER_PORT

class GDBInterfaceService(Service):
    """A class to expose a python gdb module from a running instance of gdb.
    The returned object can then be monkey-patched to remotely access objects
    from the debugged environment.
    """

    def __init__(self, conn):
        super(GDBInterfaceService, self).__init__(conn)
    
    def on_connect(self):
        super(GDBInterfaceService, self).on_connect()
        self._conn._config.update(dict(
            allow_all_attrs = True,
            allow_getattr = True,
        ))

    def on_disconnect(self):
        super(GDBInterfaceService, self).on_connect()

    def exposed_gdb(self):
        return gdb

if __name__ == "__main__":
    try:
        server = ThreadedServer(GDBInterfaceService,
                                hostname=DEFAULT_HOSTNAME, 
                                port=DEFAULT_SERVER_PORT)
        server.start()
    except socket.error, msg:
        sys.stderr.write("[SOCKET ERROR] %s\n" % msg[1])
    gdb.execute('quit')
