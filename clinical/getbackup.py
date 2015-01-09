#!/usr/bin/python
#
#
import sys
import MySQLdb as mysql
import time
import glob
import re
import socket
import os
import select
from dbaccess import *
import subprocess
import psutil

# ssh -fN -L 3307:localhost:3306 hiseq.clinical@clinical-db.scilifelab.se
cmnd = ['ssh', '-f', '-N', '-L', '3307:localhost:3306', 'hiseq.clinical@clinical-db.scilifelab.se']
# ["ssh", "%s" % HOST, COMMAND]

ssh_process = subprocess.Popen(cmnd,
                       shell=False
 #                      stdin=subprocess.PIPE,
 #                      stdout=subprocess.PIPE,
 #                      stderr=subprocess.PIPE
                       )
#result = ssh.stdout.readlines()
#if result == []:
#    error = ssh.stderr.readlines()
#    print >>sys.stderr, "ERROR: %s" % error
#else:
#    print result
print str(ssh_process.pid)

while True:
  p = ssh_process.poll()
  if p is not None: break
  time.sleep(1)

if p == 0:
        # Unfortunately there is no direct way to get the pid of the spawned ssh process, so we'll find it
        # by finding a matching process using psutil.    proc.cmdline == tunnel_cmd.split() and 
 
  current_username = psutil.Process(os.getpid()).username
  ssh_processes = [proc for proc in psutil.get_process_list() if proc.username == current_username]
  for pc in psutil.get_process_list():
    print str(pc.cmdline)
 
  if len(ssh_processes) == 1:
    print ssh_processes[0]
  else:
    raise RuntimeError, 'multiple (or zero?) tunnel ssh processes found: ' + str(ssh_processes) 
else:
  raise RuntimeError, 'Error creating tunnel: ' + str(p) + ' :: ' + str(ssh_process.stdout.readlines())



pars = readconfig('hej')
print pars['CLINICALDBUSER']

cnx, cursor = dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD'])



_VERSION_ = pars['DBVERSION']
cursor.execute(""" SELECT major, minor, patch FROM version ORDER BY time DESC LIMIT 1 """)
row = cursor.fetchone()
if row is not None:
  major = row[0]
  minor = row[1]
  patch = row[2]
else:
  sys.exit("Incorrect DB, version not found.")
if (str(major)+"."+str(minor)+"."+str(patch) == _VERSION_):
  print pars['STATSDB'] + " Correct database version "+str(_VERSION_)+"   DB "+pars['STATSDB']
else:
  exit (pars['STATSDB'] + "Incorrect DB version. This script is made for "+str(_VERSION_)+" not for "
         +str(major)+"."+str(minor)+"."+str(patch))

dbclose(cnx, cursor)

p = ssh_process.poll()
print str(p)
ssh_process.terminate()

exit(0)
