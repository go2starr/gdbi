"""
rpyc server to be run in gdb process
"""
import gdb
import sys
import rpyc
import socket
import time

from rpyc.utils.server import ThreadedServer
from rpyc import Service, restricted

from gdbi.gdbi import DEFAULT_HOSTNAME
from gdbi.gdbi import DEFAULT_SERVER_PORT
from gdbi.gdbi import SERVER_TIMEOUT

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

def start(server):
    for i in range(SERVER_TIMEOUT):
        try:
            server.start()
            return
        except socket.error, msg:
            time.sleep(1)
    sys.stderr.write("[SOCKET ERROR] %s\n" % msg[1])

if __name__ == "__main__":
    server = ThreadedServer(GDBInterfaceService,
                            hostname=DEFAULT_HOSTNAME,
                            port=DEFAULT_SERVER_PORT)
    start(server)
    gdb.execute('quit')
