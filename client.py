"""
client.py - a simple rpyc client
"""
import rpyc

from conf import DEFAULT_HOSTNAME

class GDBiClient(object):
    def __init__(self, hostname=DEFAULT_HOSTNAME):
        self.hostname = hostname

    def connect(self):
        self.conn = rpyc.classic.connect(self.hostname)
        return self.conn


if __name__ == "__main__":
    c = GDBiClient()
    conn = c.connect()
    conn.execute("print 'Hello, world!'")  # Executed in gdb

