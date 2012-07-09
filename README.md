gdbi
====

An RPC framework for interacting with a GDB python interpreter

## Problem  
Debugging an active process or core dump using python requires using
GDB's built-in python interpreter.  This requires gdb to be the
top-level process rather than gdb's subprocess.

## Solution  
RPyC offers a simple RPC framework in python.  By starting an rpc
server in the gdb process, gdb can be manipulated using a remote 'gdb'
object.

## High level overview  

*  gdbi creates the gdb process  
*  The gdb process starts an rpc server  
*  Calls can be made to the rpc server, and the results will be passed
   to the caller

## Usage  
    from gdbi import GDBInterface

    g = GDBInterface(opts=<[your,opts,here])
    with g as gdb:  # Starts gdb and rpyc server
         # Do stuff with gdb object
         print gdb.execute('help')

