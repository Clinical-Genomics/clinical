#!/usr/bin/env python
# -*- coding: utf-8 -*-
import errno
import sys
import MySQLdb as mysql
import MySQLdb.cursors
import time
import glob
import re
import socket
import os
import select
import psutil
import subprocess

def readconfig( config ):
  if os.path.isfile(config):
    Configfile = config
  else:
    Configfile = "/home/hiseq.clinical/.scilifelabrc"
  Params = {}
  with open(Configfile, "r") as Confs:
    for line in Confs:
      if len(line) > 5 and not line[0] == "#":
        line = line.rstrip()
        pv = line.split(" ")
        if len(pv) > 1:
          arg = pv[0]
          pv.pop(0)
          Params[arg] = ' '.join(pv)
        else:
          Params[pv[0]] = pv[1]
  return Params

def create_tunnel(tunnel_cmd):
  ssh_process = subprocess.Popen(tunnel_cmd,  universal_newlines=True,
                                                shell=True,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                stdin=subprocess.PIPE)
    # Assuming that the tunnel command has "-f" and "ExitOnForwardFailure=yes", then the 
    # command will return immediately so we can check the return status with a poll().
  while True:
    p = ssh_process.poll()
    if p is not None: break
    time.sleep(1)
  if p == 0:
        # Unfortunately there is no direct way to get the pid of the spawned ssh process, so we'll find it
        # by finding a matching process using psutil.
    current_username = psutil.Process(os.getpid()).username()
    ssh_processes = [proc for proc in psutil.get_process_list() if proc.cmdline() == tunnel_cmd.split() and proc.username() == current_username]
    if len(ssh_processes) == 1:
      return ssh_processes[0]
    else:
      raise RuntimeError, 'multiple (or zero?) tunnel ssh processes found: ' + str(ssh_processes) 
  else:
    raise RuntimeError, 'Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines())

def dbconnect( Host, Port, Db, User, Passwd): 
  Cnx = mysql.connect(user=User, port=int(Port), host=Host, passwd=Passwd, db=Db, cursorclass=mysql.cursors.DictCursor)
  Cursor = Cnx.cursor()
  return Cnx, Cursor

def dbclose( Cnx, Cursor):
  Cursor.close()
  Cnx.close()
  return

def generalquery( cursor, query ):
  try:
    cursor.execute(query)
  except mysql.IntegrityError, e: 
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("DB error")
# handle a specific error condition
  except mysql.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    exit("Syntax error")
# handle a generic error condition
  except mysql.Warning, e:
    exit("MySQL warning")
# handle warnings, if the cursor you're using raises them
  respons = cursor.fetchall()
  return respons 
  
  
