"""
rpyc server to be run in gdb process
"""
import gdb
import sys
import rpyc
from rpyc.utils.server import ThreadedServer
from rpyc import Service, restricted

from conf import DEFAULT_HOSTNAME
from conf import DEFAULT_SERVER_PORT

class GDBiService(Service):
    """A class to expose a python gdb module from a running instance of gdb.
    The returned object can then be monkey-patched to remotely access objects
    from the debugged environment.
    """

    def __init__(self, conn):
        super(GDBiService, self).__init__(conn)
    
    def on_connect(self):
        super(GDBiService, self).on_connect()
        self._conn._config.update(dict(
            allow_all_attrs = True,
            allow_getattr = True,
        ))

    def on_disconnect(self):
        super(GDBiService, self).on_connect()

    def exposed_gdb(self):
        return gdb

server = ThreadedServer(GDBiService, hostname=DEFAULT_HOSTNAME, port=DEFAULT_SERVER_PORT)
        
if __name__ == "__main__":
    server.start()
    gdb.execute('quit')
