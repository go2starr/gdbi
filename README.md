gdbi
====

An RPC framework for interacting with a GDB python interpreter

## Problem  
Debugging an active process or core dump using python requires using
GDB's python interpreter.  This requires gdb to be the top-level
process rather than gdb's subprocess.

## Solution  
--> monkeypatch

## High level overview  

*  gdbi creates the gdb process  
*  The gdb process starts an rpc server  
*  Calls can be made to the rpc server, and the results will be passed
   to the caller
