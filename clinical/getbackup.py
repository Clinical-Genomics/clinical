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

tunnel_pid = create_tunnel(cmnd)

pars = readconfig('hej')
print pars['CLINICALDBUSER']

cnx, cursor = dbconnect(pars['CLINICALDBHOST'], pars['CLINICALDBPORT'], pars['STATSDB'], 
                        pars['CLINICALDBUSER'], pars['CLINICALDBPASSWD'])

cmd = """ SELECT major, minor, patch FROM version ORDER BY time DESC LIMIT 1 """

_VERSION_ = pars['DBVERSION']
cursor.execute(cmd)
row = cursor.fetchone()
if row is not None:
  major = int(row['major'])
  minor = int(row['minor'])
  patch = int(row['patch'])
  print str(major), str(minor), str(patch)
else:
  sys.exit("Incorrect DB, version not found.")
if (str(major)+"."+str(minor)+"."+str(patch) == _VERSION_):
  print pars['STATSDB'] + " Correct database version "+str(_VERSION_)+"   DB "+pars['STATSDB']
else:
  exit (pars['STATSDB'] + "Incorrect DB version. This script is made for "+str(_VERSION_)+" not for "
         +str(major)+"."+str(minor)+"."+str(patch))

cmd2 = """ SELECT major, minor, patch FROM version ORDER BY time """
results = generalquery(cursor, cmd2)

dbclose(cnx, cursor)

#p = ssh_process.poll()
#print str(p), tunnel_pid
tunnel_pid.terminate()

exit(0)
