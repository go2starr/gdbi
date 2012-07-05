gdbi
====

An RPC framework for interacting with a GDB python interpreter

## Problem  
Debugging an active process or core dump using python requires using
GDB's python interpreter.  This prohibits the creation of compiled
binaries which use reults from GDB.

## Solution  
gdbi provides an rpc interface to execute arbitrary python
instructions from within a running gdb instance's python interpreter.
The results of these evaluations should be python objects which are
usable in the calling thread.

## High level overview  

*  gdbi creates the gdb process  
*  The gdb process starts an rpc server  
*  Calls can be made to the rpc server, and the results will be passed
*  to the caller
